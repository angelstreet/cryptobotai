from web3 import Web3

POLYGON_CONFIG = {
    'network_name': 'Polygon Mainnet',
    'rpc_url': 'https://polygon-rpc.com',
    'chain_id': 137,
    'currency_symbol': 'MATIC',
    'block_explorer': 'https://polygonscan.com',
    'tokens': {
        'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
        'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6'
    }
}

class PolygonSetup:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(POLYGON_CONFIG['rpc_url']))
        self.chain_id = POLYGON_CONFIG['chain_id']
    
    def prepare_metamask_connection(self):
        return {
            'network_params': {
                'chainId': hex(self.chain_id),
                'chainName': POLYGON_CONFIG['network_name'],
                'nativeCurrency': {
                    'name': 'MATIC',
                    'symbol': 'MATIC',
                    'decimals': 18
                },
                'rpcUrls': [POLYGON_CONFIG['rpc_url']],
                'blockExplorerUrls': [POLYGON_CONFIG['block_explorer']]
            }
        } 