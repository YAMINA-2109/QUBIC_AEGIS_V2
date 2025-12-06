"""
Agent Data Collector - Collects and processes Qubic blockchain data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import requests
from app.models.transaction import Transaction


class AgentCollector:
    """
    Collects data from Qubic RPC/Testnet
    Transforms raw blockchain data into features for analysis
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        """
        Initialize the collector
        
        Args:
            rpc_url: Qubic RPC endpoint URL (if we have access to the RPC, or we can use mock if None) 
        """
        self.rpc_url = rpc_url or "https://testnet.qubic.li/rpc"  # Default testnet
        self.collected_blocks: List[Dict] = []
        self.collected_transactions: List[Transaction] = []
        self.feature_cache: Dict[str, Any] = {}
    
    async def fetch_block(self, block_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch a block from Qubic network
        
        Args:
            block_number: Block number to fetch (latest if None)
            
        Returns:
            Block data dictionary
        """
        try:
            # For demo: WE return mock data
            # In production:WE use actual RPC call
            if self.rpc_url and "testnet" in self.rpc_url:
                # Mock implementation - replace with real RPC
                return {
                    "number": block_number or 8923456,
                    "timestamp": datetime.now().isoformat(),
                    "transactions": [],
                    "hash": f"0x{hash(str(block_number or 8923456)):064x}",
                }
        except Exception as e:
            print(f"Error fetching block: {e}")
            return {}
    
    async def fetch_recent_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch recent transactions from Qubic network
        
        Args:
            limit: Number of transactions to fetch
            
        Returns:
            List of transaction dictionaries
        """
        try:
            # Mock implementation - replace with real RPC
            return []
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def extract_features(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Extract features from a transaction for ML/prediction
        
        Args:
            transaction: Transaction to extract features from
            
        Returns:
            Feature dictionary
        """
        # Calculate amount_log using logarithm for feature engineering
        amount_log = 0.0
        if transaction.amount > 0:
            try:
                amount_log = math.log2(transaction.amount)
            except (ValueError, OverflowError):
                amount_log = 0.0
        
        return {
            "amount": transaction.amount,
            "amount_log": amount_log,
            "is_self_transfer": transaction.source_id == transaction.dest_id,
            "transaction_type": transaction.type,
            "tick": transaction.tick,
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else None,
            "source_id_hash": hash(transaction.source_id) % 10000,  # Anonymized
            "dest_id_hash": hash(transaction.dest_id) % 10000,  # Anonymized
        }
    
    def build_wallet_features(self, wallet_id: str, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Build aggregated features for a wallet
        
        Args:
            wallet_id: Wallet address
            transactions: List of transactions involving this wallet
            
        Returns:
            Wallet feature dictionary
        """
        if not transactions:
            return {}
        
        amounts = [tx.amount for tx in transactions]
        unique_counterparts = len(set(
            tx.dest_id if tx.source_id == wallet_id else tx.source_id
            for tx in transactions
        ))
        
        return {
            "wallet_id": wallet_id,
            "transaction_count": len(transactions),
            "total_volume": sum(amounts),
            "avg_amount": sum(amounts) / len(amounts) if amounts else 0,
            "max_amount": max(amounts) if amounts else 0,
            "min_amount": min(amounts) if amounts else 0,
            "unique_counterparts": unique_counterparts,
            "frequency": len(transactions) / 3600,  # Transactions per hour (assuming 1h window)
        }

