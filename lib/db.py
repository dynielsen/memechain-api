from tinydb import TinyDB, Query


class Index(object):
    def __init__(self, table, *keys, **kwargs):
        self.table = table
        self.keys = keys
        self.reverse = bool(kwargs.get('reverse'))

    def can_index(self, datum):
        return all(key in datum for key in self.keys)

    def all(self):
        for item in self.table.all():
            if self.can_index(item):
                yield item

    @property
    def keyfunc(self):
        def function(datum):
            return tuple(datum[k] for k in self.keys)
        return function

    def ranked(self):
        records = list(self.all())
        records.sort(
            key=self.keyfunc,
            reverse=self.reverse,
        )
        return records

    def __iter__(self):
        for item in self.ranked():
            yield item

    def __getitem__(self, idx):
        return self.ranked()[idx]


class MemeChainDB(object):
    def __init__(self, db_path):
        self._db = TinyDB(db_path)

    def add_meme(self, ipfs_id, hashlink, txid, block, imgformat):
        self._db.insert({"ipfs_id": ipfs_id, "hashlink": hashlink,
                         "txid": txid, "block": block, "imgformat": imgformat})

    def remove_meme(self, ipfs_id):
        self._db.remove(Query().ipfs_id == ipfs_id)

    def get_memechain_height(self):
        return len(self._db)

    def search_by_block(self, block):
        """
        Get a meme entry using block number as the search parameter

        block - Int
        """
        return self._db.get(Query().block == block)

    def search_by_memechain_height(self, height):
        """
        Get a meme entry using height as the search parameter

        height - Float (0 is genesis)
        """
        if height == 0:
            return None
        else:
            return Index(self._db)[height]

    def search_by_ipfs_id(self, ipfs_id):
        """
                Get a meme entry using its IPFS ID as the search parameter

                ipfs_id - String
                """
        return self._db.get(Query().ipfs_id == ipfs_id)

    def search_by_txid(self, txid):
        """
        Get a meme entry using its Kekcoin txid as the search parameter

        txid - String
        """
        return self._db.get(Query().txid == txid)

    def get_prev_block_memes(self):
        """
        Get an array with the memes in the previous kekcoin block
        """
        memechain_height = self.get_memechain_height()

        if memechain_height == 0:
            return None

        else:
            last_meme = self.search_by_memechain_height(memechain_height)

            return self._db.get(Query().block == last_meme["block"])
