"""
Qubic Realistic Simulation Service
Simulates realistic Qubic blockchain transactions with attack patterns
for comprehensive testing and demo purposes
"""
import random
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.models.transaction import Transaction
import json
import os
import string


class QubicSimulation:
    """
    Realistic Qubic transaction simulation
    Generates transactions that mimic real Qubic network behavior
    with various attack patterns and normal operations
    """
    
    def __init__(self):
        """Initialize the simulation"""
        self.tick_counter = 8923456  # Starting tick (realistic Qubic tick)
        self.wallet_pool: List[str] = []
        self.whale_wallets: List[str] = []
        self.normal_wallets: List[str] = []
        self.mixer_wallets: List[str] = []
        self._initialize_wallet_pool()
        
        # Attack patterns to simulate
        self.attack_scenarios = [
            "normal",
            "normal",
            "normal",
            "normal",
            "normal",
            "normal",
            "normal",
            "normal",
            "whale_transfer",      # 1 in 10
            "suspicious_pattern",   # 1 in 10
        ]
        
        # Timing - Optimal balance for demo (not too frequent, not too rare)
        self.last_attack_tick = 0
        self.attack_interval = 30  # Initial short interval to show system at start
        self.attack_count = 0  # Attack counter to reduce after initial phase
        self.warmup_complete = False  # Initial phase with more attacks
        
        # Token pool for Qubic ecosystem (based on Qubictrade.com)
        self.token_pool = [
            {"symbol": "QX", "name": "Qubic"},
            {"symbol": "QXALPHA", "name": "Qubic Alpha"},
            {"symbol": "QU", "name": "Qubic Units"},
            {"symbol": "QXTRADE", "name": "Qubic Trade Token"},
            {"symbol": "QUBICX", "name": "Qubic Extended"},
        ]
    
    def _get_random_token(self) -> Optional[Dict[str, str]]:
        """
        Get a random token or None with V2 Market Intelligence distribution
        - 30% QXALPHA (for demo scenario)
        - 70% other tokens or None
        """
        rand = random.random()
        if rand < 0.30:  # 30% QXALPHA for demo
            return {"symbol": "QXALPHA", "name": "Qubic Alpha"}
        elif rand < 0.70:  # 40% other tokens
            # Filter out QXALPHA from pool for this case
            other_tokens = [t for t in self.token_pool if t["symbol"] != "QXALPHA"]
            return random.choice(other_tokens) if other_tokens else None
        else:  # 30% no token (simple QUBIC transfer)
            return None
        
    def _initialize_wallet_pool(self):
        """Initialize realistic wallet pool"""
        # Generate realistic Qubic wallet addresses (base32 encoded, 55 chars)
        # Format: Similar to Qubic addresses
        for i in range(100):
            wallet_id = self._generate_qubic_wallet_id(i)
            self.wallet_pool.append(wallet_id)
            if i < 5:
                self.whale_wallets.append(wallet_id)
            elif i < 15:
                self.mixer_wallets.append(wallet_id)
            else:
                self.normal_wallets.append(wallet_id)
    
    def _generate_qubic_wallet_id(self, index: int) -> str:
        """Generate a realistic-looking Qubic wallet ID"""
        # Qubic addresses are base32 encoded, typically 55 characters
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"  # Base32 alphabet
        # Generate deterministic but realistic-looking addresses
        random.seed(index * 42)  # Deterministic seed
        address = ''.join(random.choice(chars) for _ in range(55))
        return address
    
    async def generate_realistic_transaction(self) -> Transaction:
        """
        Generate a realistic Qubic transaction
        Mimics real network patterns with occasional attacks
        """
        self.tick_counter += 1
        
        # Decide transaction type based on tick and patterns
        scenario = self._select_scenario()
        
        if scenario == "whale_transfer":
            return self._generate_whale_transaction()
        elif scenario == "suspicious_pattern":
            return self._generate_suspicious_transaction()
        elif scenario == "wash_trading":
            return self._generate_wash_trading()
        elif scenario == "flash_loan_pattern":
            return self._generate_flash_loan_pattern()
        elif scenario == "spam_attack":
            return self._generate_spam_transaction()
        else:
            return self._generate_normal_transaction()
    
    def _select_scenario(self) -> str:
        """Select transaction scenario based on current state"""
        # Periodic attack patterns
        if self.tick_counter - self.last_attack_tick > self.attack_interval:
            self.last_attack_tick = self.tick_counter
            self.attack_count += 1
            
            attack_type = random.choice([
                "whale_transfer",
                "suspicious_pattern",
                "wash_trading",
                "flash_loan_pattern",
                "spam_attack",
            ])
            
            # Initial phase (first 3-4 attacks): frequent to show the system
            if self.attack_count <= 4:
                self.attack_interval = random.randint(30, 45)  # Frequent at start
            else:
                # After initial phase: much less frequent to allow demos
                self.warmup_complete = True
                self.attack_interval = random.randint(150, 250)  # Much less frequent after
            
            return attack_type
        
        # Random selection from pool
        return random.choice(self.attack_scenarios)
    
    def _generate_normal_transaction(self) -> Transaction:
        """Generate a normal Qubic transaction"""
        source = random.choice(self.normal_wallets)
        dest = random.choice(self.wallet_pool)
        # Avoid self-transfers in normal transactions
        while dest == source:
            dest = random.choice(self.wallet_pool)
        
        amount = random.uniform(100, 10000)  # Normal amounts
        token_info = self._get_random_token()  # 70% chance to include token
        
        return Transaction(
            source_id=source,
            dest_id=dest,
            amount=round(amount, 8),
            tick=self.tick_counter,
            type="transfer",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_whale_transaction(self) -> Transaction:
        """Generate a whale transaction (large amount)"""
        whale = random.choice(self.whale_wallets)
        dest = random.choice(self.wallet_pool)
        
        # Whale amounts: 50k - 500k QUBIC
        amount = random.uniform(50000, 500000)
        
        # V2: 50% chance for QXALPHA in whale transactions (high risk signals)
        if random.random() < 0.50:
            token_info = {"symbol": "QXALPHA", "name": "Qubic Alpha"}
        else:
            token_info = self._get_random_token()
        
        return Transaction(
            source_id=whale,
            dest_id=dest,
            amount=round(amount, 8),
            tick=self.tick_counter,
            type="transfer",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_suspicious_transaction(self) -> Transaction:
        """Generate a suspicious transaction pattern"""
        # Self-transfer (potential wash trading)
        wallet = random.choice(self.normal_wallets + self.whale_wallets)
        
        token_info = self._get_random_token()
        
        return Transaction(
            source_id=wallet,
            dest_id=wallet,  # Self-transfer
            amount=round(random.uniform(5000, 50000), 8),
            tick=self.tick_counter,
            type="wash_trading",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_wash_trading(self) -> Transaction:
        """Generate wash trading pattern"""
        # Rapid back-and-forth between wallets
        wallet1 = random.choice(self.normal_wallets)
        wallet2 = random.choice(self.normal_wallets)
        while wallet2 == wallet1:
            wallet2 = random.choice(self.normal_wallets)
        
        token_info = self._get_random_token()
        
        return Transaction(
            source_id=wallet1,
            dest_id=wallet2,
            amount=round(random.uniform(1000, 10000), 8),
            tick=self.tick_counter,
            type="wash_trading",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_flash_loan_pattern(self) -> Transaction:
        """Generate flash loan attack pattern"""
        attacker = random.choice(self.normal_wallets)
        mixer = random.choice(self.mixer_wallets)
        
        # Large amount through mixer (potential laundering)
        amount = random.uniform(100000, 1000000)
        token_info = self._get_random_token()  # Flash loans often target specific tokens
        
        return Transaction(
            source_id=attacker,
            dest_id=mixer,
            amount=round(amount, 8),
            tick=self.tick_counter,
            type="flash_loan",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_spam_transaction(self) -> Transaction:
        """Generate spam transaction"""
        # High frequency, small amounts
        source = random.choice(self.normal_wallets)
        dest = random.choice(self.wallet_pool)
        token_info = self._get_random_token()  # Spam can target any token
        
        return Transaction(
            source_id=source,
            dest_id=dest,
            amount=round(random.uniform(0.1, 10), 8),  # Very small
            tick=self.tick_counter,
            type="spam",
            signature=self._generate_signature(),
            timestamp=datetime.now(),
            token_symbol=token_info["symbol"] if token_info else None,
            token_name=token_info["name"] if token_info else None
        )
    
    def _generate_signature(self) -> str:
        """Generate realistic transaction signature"""
        # Qubic signatures are typically 88 characters (base32)
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        return ''.join(random.choice(chars) for _ in range(88))


class QubicDataReplay:
    """
    Replay real Qubic transaction data from JSON file
    Useful for demos with authentic transaction patterns
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize replay from file
        
        Args:
            data_file: Path to JSON file with transaction data
        """
        self.data_file = data_file or "backend/app/services/qubic_transactions_sample.json"
        self.transactions: List[Dict[str, Any]] = []
        self.current_index = 0
        self._load_data()
    
    def _load_data(self):
        """Load transaction data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.transactions = json.load(f)
                # File loaded successfully
            except Exception as e:
                # Error loading file - will use simulation mode
                self.transactions = []
        else:
            # File not found - will use simulation mode
            self.transactions = []
    
    async def get_next_transaction(self) -> Optional[Transaction]:
        """Get next transaction from replay"""
        if not self.transactions:
            return None
        
        if self.current_index >= len(self.transactions):
            self.current_index = 0  # Loop back
        
        tx_data = self.transactions[self.current_index]
        self.current_index += 1
        
        # Convert to Transaction model
        try:
            return Transaction(
                source_id=tx_data.get("source_id", ""),
                dest_id=tx_data.get("dest_id", ""),
                amount=float(tx_data.get("amount", 0)),
                tick=int(tx_data.get("tick", 0)),
                type=tx_data.get("type", "transfer"),
                signature=tx_data.get("signature", ""),
                timestamp=datetime.fromisoformat(tx_data.get("timestamp", datetime.now().isoformat()))
            )
        except Exception as e:
            # Error parsing transaction - skip it
            return None

