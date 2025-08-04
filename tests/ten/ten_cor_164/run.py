from collections import Counter
from ten.test.basetest import TenNetworkTest


class PySysTest(TenNetworkTest):

    def execute(self):
        # fetch latest batch to use for search
        batch_header = self.scan_get_latest_batch()
        batch = self.scan_get_batch(hash=batch_header['hash'])

        hashSearch = self.scan_search(batch['Header']['hash'])
         # assert search by hash returns the correct batch 
        self.assertTrue(hashSearch['result']['Total'] == 1,
                    assertMessage='Search by hash should return exactly 1 result in resultsData')
        self.assertTrue(hashSearch['result']['ResultsData'][0]['type'] == 'batch',
                    assertMessage='Search by hash should return a batch type result')
        self.assertTrue(hashSearch['result']['ResultsData'][0]['hash'] == batch['Header']['hash'].replace('0x', ''),
                    assertMessage='Search by hash should return the correct batch hash')
    
         # convert hex height to decimal string for search
        batch_height_int = int(batch['Header']['number'], 16)  # Convert hex to int
        batch_height_string = str(batch_height_int)  # Convert to string
        
        # search by batch height (number)
        heightSearch = self.scan_search(batch_height_string)
        
         # assert search by height returns results - there would be more than one as it could also be sequence number
        self.assertTrue(heightSearch['result']['Total'] >= 1,
                    assertMessage='Search by height should return 1 or more results')