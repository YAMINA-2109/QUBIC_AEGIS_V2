"""
Mock data generator for Qubic blockchain transactions
Generates realistic transaction data with anomalies for testing
Enhanced with realistic Qubic simulation mode
"""
import asyncio
import random
import string
from datetime import datetime
from typing import AsyncIterator, Optional, Callable
from app.models.transaction import Transaction
import os

# Import realistic simulation
try:
    from app.services.qubic_simulation import QubicSimulation
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False


class QubicDataStream:
    """
    Generates fake Qubic transactions in real-time
    90% normal transactions, 10% anomalies (large amounts, wash trading, etc.)
    V2: Enhanced with token symbols for Market Intelligence
    """
    
    # Token pool for V2 Market Intelligence
    TOKEN_POOL = [
        ("QXALPHA", "Qubic Alpha"),  # 30% weight for demo
        ("QX", "Qubic"),
        ("CFB", "Cryptobond"),
        ("QTRY", "Qubic Treasury"),
        (None, None),  # Simple QUBIC transfer (no token)
    ]
    
    def __init__(self, interval: float = 2.0, use_realistic_simulation: bool = None):
        """
        Initialize the data stream
        
        Args:
            interval: Time interval in seconds between transaction generation (default: 2.0)
            use_realistic_simulation: Use realistic Qubic simulation (default: from env QUIBIC_REALISTIC_MODE)
        """
        self.interval = interval
        self.tick_counter = 1000
        self.account_ids = self._generate_account_pool()
        self.running = False
        self.callbacks = []
        
        # Check if we should use realistic simulation
        if use_realistic_simulation is None:
            use_realistic_simulation = os.getenv("QUBIC_REALISTIC_MODE", "true").lower() == "true"
        
        self.use_realistic = use_realistic_simulation and SIMULATION_AVAILABLE
        
        if self.use_realistic:
            self.simulation = QubicSimulation()
            print("✅ Realistic Qubic Simulation Mode ENABLED")
            print("   - Realistic wallet addresses (55-char Qubic format)")
            print("   - Attack patterns: whale transfers, wash trading, flash loans, spam")
            print("   - Periodic attack sequences for comprehensive testing")
        else:
            self.simulation = None
            print("📊 Standard Mock Mode - Simple transaction generation")
    
    def _generate_account_pool(self, count: int = 50) -> list:
        """Generate a pool of realistic account IDs"""
        accounts = []
        for _ in range(count):
            # Generate 40-character hex string (simulating Qubic account ID)
            account_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=40))
            accounts.append(account_id)
        return accounts
    
    def _generate_signature(self) -> str:
        """Generate a mock transaction signature"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=64))
    
    def _select_token(self) -> tuple:
        """
        Select a token for the transaction
        Returns: (symbol, name) tuple, with 30% chance for QXALPHA
        """
        rand = random.random()
        if rand < 0.30:  # 30% QXALPHA for demo
            return ("QXALPHA", "Qubic Alpha")
        elif rand < 0.55:  # 25% QX
            return ("QX", "Qubic")
        elif rand < 0.70:  # 15% other tokens
            return random.choice([("CFB", "Cryptobond"), ("QTRY", "Qubic Treasury")])
        else:  # 30% no token (simple QUBIC transfer)
            return (None, None)
    
    def _generate_normal_transaction(self) -> Transaction:
        """Generate a normal transaction (90% of cases) with V2 token support"""
        source = random.choice(self.account_ids)
        dest = random.choice([acc for acc in self.account_ids if acc != source])
        
        # Normal amounts: 1 to 10,000 QUBIC
        amount = round(random.uniform(1.0, 10000.0), 2)
        
        # V2: Add token symbol (30% QXALPHA for demo)
        token_symbol, token_name = self._select_token()
        
        # If QXALPHA, slightly increase chance of larger amounts (whale simulation)
        if token_symbol == "QXALPHA" and random.random() < 0.15:  # 15% chance for larger QXALPHA tx
            amount = round(random.uniform(5000.0, 50000.0), 2)
        
        self.tick_counter += 1
        
        return Transaction(
            source_id=source,
            dest_id=dest,
            amount=amount,
            tick=self.tick_counter,
            type="transfer",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            is_anomaly=False,
            token_symbol=token_symbol,
            token_name=token_name
        )
    
    def _generate_anomaly_transaction(self) -> Transaction:
        """
        Generate an anomaly transaction (10% of cases) - HIGH RISK for signals
        V2: Enhanced with token symbols for Market Intelligence
        """
        anomaly_type = random.choice(["large_amount", "wash_trading", "rapid_transfer"])
        
        # V2: Select token (anomalies often involve tokens, especially QXALPHA)
        if random.random() < 0.60:  # 60% of anomalies have tokens
            if random.random() < 0.50:  # 50% of those are QXALPHA (for demo)
                token_symbol, token_name = ("QXALPHA", "Qubic Alpha")
            else:
                token_symbol, token_name = self._select_token()
                if token_symbol is None:
                    token_symbol, token_name = ("QX", "Qubic")  # Default to QX for anomalies
        else:
            token_symbol, token_name = (None, None)
        
        if anomaly_type == "large_amount":
            # Extremely large transaction (potential whale move) - HIGH RISK
            source = random.choice(self.account_ids)
            dest = random.choice([acc for acc in self.account_ids if acc != source])
            amount = round(random.uniform(100000.0, 10000000.0), 2)
            
        elif anomaly_type == "wash_trading":
            # Same account sending to itself multiple times - HIGH RISK
            account = random.choice(self.account_ids)
            source = account
            dest = account
            amount = round(random.uniform(1000.0, 50000.0), 2)
            
        else:  # rapid_transfer
            # Very small or zero amount rapid transfer - MEDIUM RISK
            source = random.choice(self.account_ids)
            dest = random.choice([acc for acc in self.account_ids if acc != source])
            amount = round(random.uniform(0.01, 0.1), 4)
        
        self.tick_counter += 1
        
        return Transaction(
            source_id=source,
            dest_id=dest,
            amount=amount,
            tick=self.tick_counter,
            type=anomaly_type,
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            is_anomaly=True,
            token_symbol=token_symbol,
            token_name=token_name
        )
    
    def register_callback(self, callback: Callable[[Transaction], None]):
        """Register a callback function to be called when a transaction is generated"""
        self.callbacks.append(callback)
    
    async def start(self):
        """Start generating transactions"""
        self.running = True
        while self.running:
            # Generate transaction based on mode
            if self.use_realistic and self.simulation:
                transaction = await self.simulation.generate_realistic_transaction()
            else:
                # 90% normal, 10% anomaly
                if random.random() < 0.1:
                    transaction = self._generate_anomaly_transaction()
                else:
                    transaction = self._generate_normal_transaction()
            
            # Notify all registered callbacks
            for callback in self.callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(transaction)
                    else:
                        callback(transaction)
                except Exception as e:
                    print(f"Error in callback: {e}")
            
            await asyncio.sleep(self.interval)
    
    async def get_next_transaction(self) -> Transaction:
        """Get next transaction (synchronous-style async)"""
        if self.use_realistic and self.simulation:
            return await self.simulation.generate_realistic_transaction()
        else:
            if random.random() < 0.1:
                return self._generate_anomaly_transaction()
            else:
                return self._generate_normal_transaction()
    
    async def stream(self) -> AsyncIterator[Transaction]:
        """Async generator that yields transactions"""
        while True:
            if self.use_realistic and self.simulation:
                # Use realistic simulation
                transaction = await self.simulation.generate_realistic_transaction()
            else:
                # Use standard mock generation
                if random.random() < 0.1:
                    transaction = self._generate_anomaly_transaction()
                else:
                    transaction = self._generate_normal_transaction()
            
            yield transaction
            await asyncio.sleep(self.interval)
    
    def stop(self):
        """Stop generating transactions"""
        self.running = False

