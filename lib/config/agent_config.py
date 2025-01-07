class AgentConfig:
    def __init__(self, config_name):
        self.config_name = config_name
        self.config = self._load_config(config_name)
        self._validate_config()
    
    def _load_config(self, config_name):
        """Load configuration based on the config name"""
        # Define default configurations
        configs = {
            'aggressive': {
                'risk_level': 'high',
                'max_position_size': 1.0,
                'stop_loss': 0.05,
                'take_profit': 0.1
            },
            'conservative': {
                'risk_level': 'low',
                'max_position_size': 0.5,
                'stop_loss': 0.02,
                'take_profit': 0.04
            }
        }
        
        if config_name not in configs:
            raise ValueError(f"Invalid config name: {config_name}. Available configs: {list(configs.keys())}")
            
        return configs[config_name]
    
    def _validate_config(self):
        """Validate the configuration parameters"""
        required_fields = ['risk_level', 'max_position_size', 'stop_loss', 'take_profit']
        
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required configuration field: {field}")
        
        # Validate value ranges
        if not 0 < self.config['max_position_size'] <= 1:
            raise ValueError("max_position_size must be between 0 and 1")
        if not 0 < self.config['stop_loss'] < 1:
            raise ValueError("stop_loss must be between 0 and 1")
        if not 0 < self.config['take_profit'] < 1:
            raise ValueError("take_profit must be between 0 and 1")