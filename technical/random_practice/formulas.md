shard_id = hash(chat_id) % N, where N is no. of shards
Partition_id = hash(key) % N, where N is no of partitions