"""
Qubic Data Ingestion Layer (Teammate's Work)
QubicRPCCollector: Asynchronous, stable data collector for QUBIC AEGIS
"""
import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class QubicRPCCollector:
    """
    Qubic RPC Data Collector - Blockchain Ingestion Layer
    
    Key Features:
    - Asynchronous HTTP client using httpx
    - Automatic failover between 3 RPC endpoints
    - Robust error handling
    """
    
    def __init__(self):
        """Initialize with production endpoints"""
        self.base_urls = [
            "https://rpc.qubic.org/v1",          # Production (Primary)
            "https://testnet-rpc.qubic.org/v1",  # Testnet (Backup 1)
            "https://rpc-staging.qubic.org/v2"   # Staging (Backup 2)
        ]
        self.current_url_index = 0
        self._client: Optional[httpx.AsyncClient] = None
        logger.info(f"QubicRPCCollector initialized. Primary: {self.base_urls[0]}")

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    def _get_current_url(self) -> str:
        return self.base_urls[self.current_url_index]

    def _switch_endpoint(self):
        """Failover logic: Switch to next available RPC"""
        old_url = self._get_current_url()
        self.current_url_index = (self.current_url_index + 1) % len(self.base_urls)
        logger.warning(f"⚠️ Switching RPC endpoint: {old_url} -> {self._get_current_url()}")

    async def get_latest_tick(self) -> Optional[int]:
        """Fetch the latest tick number"""
        if not self._client:
            # Create temporary client if not in context manager
            async with httpx.AsyncClient() as client:
                return await self._fetch_tick_internal(client)
        return await self._fetch_tick_internal(self._client)

    async def _fetch_tick_internal(self, client: httpx.AsyncClient) -> Optional[int]:
        """Internal retry logic for fetching tick"""
        for _ in range(len(self.base_urls)):
            url = f"{self._get_current_url()}/tick-info"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Handle different API response formats
                tick = None
                if 'tickInfo' in data:
                    tick = data['tickInfo'].get('tick')
                elif 'tick' in data:
                    tick = data.get('tick')
                elif 'currentTick' in data:
                    tick = data.get('currentTick')
                
                if tick:
                    return int(tick)
            except Exception as e:
                logger.error(f"Error fetching tick from {url}: {e}")
                self._switch_endpoint()
        
        return None

    async def collect_latest_data(self) -> List[Dict[str, Any]]:
        """
        Main function used by AEGIS Pipeline.
        Fetches transactions from the latest Tick.
        """
        # Ensure we have a client
        local_client = False
        if not self._client:
            self._client = httpx.AsyncClient(timeout=10.0)
            local_client = True

        try:
            # 1. Get Latest Tick
            latest_tick = await self._fetch_tick_internal(self._client)
            if not latest_tick:
                return []

            # 2. Get Transactions for this Tick
            # Try endpoints structure (v1 vs v2)
            endpoints = [
                f"/ticks/{latest_tick}/transactions", # V2
                f"/tick-transactions/{latest_tick}"   # V1
            ]
            
            transactions = []
            success = False

            for _ in range(len(self.base_urls)):
                base = self._get_current_url()
                for ep in endpoints:
                    try:
                        url = f"{base}{ep}".replace("/v1/v2", "/v2") # Clean url
                        response = await self._client.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            # Parse data
                            if isinstance(data, list): transactions = data
                            elif 'transactions' in data: transactions = data['transactions']
                            elif 'data' in data: transactions = data['data']
                            
                            success = True
                            break
                    except Exception:
                        continue
                
                if success: break
                self._switch_endpoint()

            # 3. Normalize Data using Teammate's logic
            normalized_data = []
            for tx in transactions:
                norm = normalize_transaction_data(tx, latest_tick)
                if norm:
                    normalized_data.append(norm)
            
            return normalized_data

        finally:
            if local_client and self._client:
                await self._client.aclose()
                self._client = None

# --- Helper Function (Outside Class) ---

def normalize_transaction_data(raw_tx: Dict[str, Any], tick: int) -> Optional[Dict[str, Any]]:
    """
    Standardizes transaction format for the AI Pipeline.
    Adapted from teammate's work.
    """
    try:
        # Handle different RPC response formats
        src = raw_tx.get('sourceId') or raw_tx.get('sourcePublicKey') or "UNKNOWN"
        dst = raw_tx.get('destId') or raw_tx.get('destPublicKey') or "UNKNOWN"
        amt = float(raw_tx.get('amount', 0))
        
        # Detect Protocol / Contract Interactions
        inputType = raw_tx.get('inputType', 0)
        
        return {
            "source_address": src,
            "destination_address": dst,
            "amount": amt,
            "tick_number": tick,
            "timestamp": datetime.now().timestamp(), # Real time
            "input_type": inputType,
            "raw": raw_tx
        }
    except Exception as e:
        logger.error(f"Normalization error: {e}")
        return None