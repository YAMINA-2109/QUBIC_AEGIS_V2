"""
Test Data Generator - Generates realistic Qubic transaction datasets for testing
This creates a persistent database-like structure for comprehensive testing
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.models.transaction import Transaction
from app.services.qubic_simulation import QubicSimulation


class TestDataGenerator:
    """
    Generates and manages realistic test data for QUBIC AEGIS
    Can work with JSON files or in-memory database
    """
    
    def __init__(self, data_dir: str = "test_data"):
        """
        Initialize the test data generator
        
        Args:
            data_dir: Directory to store test data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.transactions_file = self.data_dir / "transactions.json"
        self.wallets_file = self.data_dir / "wallets.json"
        self.scenarios_file = self.data_dir / "attack_scenarios.json"
        
        self.simulation = QubicSimulation()
        self.transactions: List[Dict[str, Any]] = []
        self.wallets: Dict[str, Dict[str, Any]] = {}
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing test data from files"""
        if self.transactions_file.exists():
            try:
                with open(self.transactions_file, 'r') as f:
                    self.transactions = json.load(f)
            except Exception as e:
                print(f"Error loading transactions: {e}")
                self.transactions = []
        
        if self.wallets_file.exists():
            try:
                with open(self.wallets_file, 'r') as f:
                    self.wallets = json.load(f)
            except Exception as e:
                print(f"Error loading wallets: {e}")
                self.wallets = {}
    
    def _save_data(self):
        """Save test data to files"""
        try:
            with open(self.transactions_file, 'w') as f:
                json.dump(self.transactions, f, indent=2, default=str)
            
            with open(self.wallets_file, 'w') as f:
                json.dump(self.wallets, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    async def generate_test_dataset(
        self,
        num_transactions: int = 1000,
        include_attacks: bool = True,
        attack_ratio: float = 0.1
    ) -> List[Transaction]:
        """
        Generate a comprehensive test dataset
        
        Args:
            num_transactions: Total number of transactions to generate
            include_attacks: Whether to include attack scenarios
            attack_ratio: Ratio of attack transactions (0.0 to 1.0)
        
        Returns:
            List of Transaction objects
        """
        print(f"🔄 Generating {num_transactions} transactions...")
        transactions = []
        num_attacks = int(num_transactions * attack_ratio) if include_attacks else 0
        
        # Generate normal transactions
        for i in range(num_transactions - num_attacks):
            tx = await self.simulation.generate_realistic_transaction()
            tx_dict = {
                "source_id": tx.source_id,
                "dest_id": tx.dest_id,
                "amount": tx.amount,
                "tick": tx.tick,
                "type": tx.type,
                "signature": tx.signature,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else datetime.now().isoformat(),
                "is_anomaly": False
            }
            self.transactions.append(tx_dict)
            transactions.append(tx)
            
            # Update wallet stats
            self._update_wallet_stats(tx.source_id, tx.amount, "source")
            self._update_wallet_stats(tx.dest_id, tx.amount, "dest")
            
            if (i + 1) % 100 == 0:
                print(f"  Generated {i + 1} normal transactions...")
        
        # Generate attack transactions
        if include_attacks:
            attack_types = ["whale_dump", "wash_trade", "flash_attack", "wallet_drain"]
            for i in range(num_attacks):
                attack_type = attack_types[i % len(attack_types)]
                # Force attack type
                tx = await self.simulation.generate_realistic_transaction()
                tx.type = attack_type
                tx.amount = self._get_attack_amount(attack_type)
                tx.is_anomaly = True
                
                tx_dict = {
                    "source_id": tx.source_id,
                    "dest_id": tx.dest_id,
                    "amount": tx.amount,
                    "tick": tx.tick,
                    "type": attack_type,
                    "signature": tx.signature,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else datetime.now().isoformat(),
                    "is_anomaly": True,
                    "attack_type": attack_type
                }
                self.transactions.append(tx_dict)
                transactions.append(tx)
                
                self._update_wallet_stats(tx.source_id, tx.amount, "source", is_attack=True)
                self._update_wallet_stats(tx.dest_id, tx.amount, "dest", is_attack=True)
                
                if (i + 1) % 10 == 0:
                    print(f"  Generated {i + 1} attack transactions...")
        
        # Save to disk
        self._save_data()
        
        print(f"✅ Generated {len(transactions)} transactions ({num_transactions - num_attacks} normal, {num_attacks} attacks)")
        print(f"💾 Data saved to {self.data_dir}")
        
        return transactions
    
    def _get_attack_amount(self, attack_type: str) -> float:
        """Get appropriate amount for attack type"""
        amounts = {
            "whale_dump": 500000.0,
            "wash_trade": 10000.0,
            "flash_attack": 1000000.0,
            "wallet_drain": 75000.0
        }
        return amounts.get(attack_type, 50000.0)
    
    def _update_wallet_stats(
        self,
        wallet_id: str,
        amount: float,
        role: str,
        is_attack: bool = False
    ):
        """Update wallet statistics"""
        if wallet_id not in self.wallets:
            self.wallets[wallet_id] = {
                "wallet_id": wallet_id,
                "total_received": 0.0,
                "total_sent": 0.0,
                "transaction_count": 0,
                "attack_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "risk_score": 0.0
            }
        
        wallet = self.wallets[wallet_id]
        if role == "source":
            wallet["total_sent"] += amount
        else:
            wallet["total_received"] += amount
        
        wallet["transaction_count"] += 1
        wallet["last_seen"] = datetime.now().isoformat()
        
        if is_attack:
            wallet["attack_count"] += 1
            wallet["risk_score"] = min(100, wallet["risk_score"] + 20)
        else:
            # Decrease risk slightly for normal transactions
            wallet["risk_score"] = max(0, wallet["risk_score"] - 1)
    
    def get_wallet_transactions(self, wallet_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all transactions for a specific wallet"""
        return [
            tx for tx in self.transactions
            if tx["source_id"] == wallet_id or tx["dest_id"] == wallet_id
        ][-limit:]
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get most recent transactions"""
        return self.transactions[-limit:]
    
    def get_attack_transactions(self) -> List[Dict[str, Any]]:
        """Get all attack transactions"""
        return [tx for tx in self.transactions if tx.get("is_anomaly", False)]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get dataset statistics"""
        total_volume = sum(tx["amount"] for tx in self.transactions)
        attack_count = sum(1 for tx in self.transactions if tx.get("is_anomaly", False))
        
        return {
            "total_transactions": len(self.transactions),
            "total_wallets": len(self.wallets),
            "total_volume": total_volume,
            "attack_count": attack_count,
            "attack_ratio": attack_count / len(self.transactions) if self.transactions else 0,
            "average_amount": total_volume / len(self.transactions) if self.transactions else 0,
            "high_risk_wallets": sum(1 for w in self.wallets.values() if w["risk_score"] > 70)
        }
    
    async def stream_transactions(
        self,
        interval: float = 2.0,
        max_transactions: Optional[int] = None
    ):
        """
        Stream transactions from the dataset asynchronously
        
        Args:
            interval: Time between transactions (seconds)
            max_transactions: Maximum number of transactions to stream (None for all)
        
        Yields:
            Transaction objects
        """
        transactions_to_stream = self.transactions
        if max_transactions:
            transactions_to_stream = transactions_to_stream[-max_transactions:]
        
        for tx_dict in transactions_to_stream:
            # Convert dict back to Transaction
            tx = Transaction(
                source_id=tx_dict["source_id"],
                dest_id=tx_dict["dest_id"],
                amount=tx_dict["amount"],
                tick=tx_dict["tick"],
                type=tx_dict["type"],
                signature=tx_dict["signature"],
                timestamp=datetime.fromisoformat(tx_dict["timestamp"]) if tx_dict.get("timestamp") else datetime.now(),
                is_anomaly=tx_dict.get("is_anomaly", False)
            )
            yield tx
            await asyncio.sleep(interval)


# Global instance
_test_data_generator: Optional[TestDataGenerator] = None


def get_test_data_generator() -> TestDataGenerator:
    """Get or create the global test data generator instance"""
    global _test_data_generator
    if _test_data_generator is None:
        _test_data_generator = TestDataGenerator()
    return _test_data_generator


async def initialize_test_data(
    num_transactions: int = 1000,
    force_regenerate: bool = False
):
    """
    Initialize test data for the system
    
    Args:
        num_transactions: Number of transactions to generate
        force_regenerate: Whether to regenerate even if data exists
    """
    generator = get_test_data_generator()
    
    if force_regenerate or len(generator.transactions) == 0:
        print("🔄 Initializing test data...")
        await generator.generate_test_dataset(
            num_transactions=num_transactions,
            include_attacks=True,
            attack_ratio=0.15  # 15% attacks
        )
    else:
        print(f"✅ Using existing test data ({len(generator.transactions)} transactions)")
    
    stats = generator.get_statistics()
    print(f"📊 Test Data Statistics:")
    print(f"   - Total Transactions: {stats['total_transactions']}")
    print(f"   - Total Wallets: {stats['total_wallets']}")
    print(f"   - Attack Transactions: {stats['attack_count']} ({stats['attack_ratio']*100:.1f}%)")
    print(f"   - High Risk Wallets: {stats['high_risk_wallets']}")

