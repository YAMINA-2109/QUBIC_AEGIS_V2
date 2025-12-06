"""
Qubic Data Replay - Replays real Qubic transactions for demo
"""
import json
import asyncio
from typing import List, Optional
from pathlib import Path
from app.models.transaction import Transaction
from datetime import datetime, timedelta


class QubicDataReplay:
    """
    Replays real Qubic transactions from a JSON file
    Used for demo purposes to show real blockchain data
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the replay system
        
        Args:
            data_file: Path to JSON file with real Qubic transactions
        """
        self.data_file = data_file or "backend/data/real_qubic_tx.json"
        self.transactions: List[Transaction] = []
        self.current_index = 0
        self.running = False
    
    def load_transactions(self) -> bool:
        """
        Load transactions from JSON file
        
        Returns:
            True if loaded successfully
        """
        try:
            file_path = Path(self.data_file)
            if not file_path.exists():
                print(f"Data file not found: {self.data_file}")
                print("Creating sample data file...")
                self._create_sample_data()
                return False
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Parse transactions
            self.transactions = []
            for tx_data in data.get("transactions", []):
                try:
                    transaction = Transaction(
                        source_id=tx_data.get("source_id", ""),
                        dest_id=tx_data.get("dest_id", ""),
                        amount=float(tx_data.get("amount", 0)),
                        tick=int(tx_data.get("tick", 0)),
                        type=tx_data.get("type", "transfer"),
                        signature=tx_data.get("signature", ""),
                        timestamp=datetime.fromisoformat(tx_data.get("timestamp")) if tx_data.get("timestamp") else datetime.now(),
                        is_anomaly=tx_data.get("is_anomaly", False),
                    )
                    self.transactions.append(transaction)
                except Exception as e:
                    print(f"Error parsing transaction: {e}")
                    continue
            
            print(f"Loaded {len(self.transactions)} transactions from {self.data_file}")
            return len(self.transactions) > 0
            
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return False
    
    def _create_sample_data(self):
        """Create sample data file if it doesn't exist"""
        file_path = Path(self.data_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        sample_data = {
            "description": "Real Qubic transactions for replay demo",
            "transactions": [
                {
                    "source_id": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                    "dest_id": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                    "amount": 5000.0,
                    "tick": 8923456,
                    "type": "transfer",
                    "signature": "sample_signature_1",
                    "timestamp": datetime.now().isoformat(),
                    "is_anomaly": False
                }
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    async def stream(self, interval: float = 2.0):
        """
        Stream transactions as async generator
        
        Args:
            interval: Time between transactions (seconds)
        """
        if not self.transactions:
            if not self.load_transactions():
                return
        
        self.running = True
        self.current_index = 0
        
        while self.running:
            if self.current_index >= len(self.transactions):
                # Loop back to start
                self.current_index = 0
            
            transaction = self.transactions[self.current_index]
            
            # Update timestamp to current time
            transaction.timestamp = datetime.now()
            
            yield transaction
            self.current_index += 1
            
            await asyncio.sleep(interval)
    
    def stop(self):
        """Stop replay"""
        self.running = False

