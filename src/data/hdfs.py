from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = ["content", "component", "level", "block_id"]
TARGET_COLUMN = "anomaly"


def generate_sample_hdfs_dataset() -> pd.DataFrame:
    rows = [
        {
            "content": "Receiving block blk_-1608999687919862906 src /10.250.19.102 dest /10.250.19.102",
            "component": "dfs.DataNode$DataXceiver",
            "level": "INFO",
            "block_id": "blk_-1608999687919862906",
            "anomaly": 0,
        },
        {
            "content": "PacketResponder 1 for block blk_-1608999687919862906 terminating",
            "component": "dfs.DataNode$PacketResponder",
            "level": "INFO",
            "block_id": "blk_-1608999687919862906",
            "anomaly": 0,
        },
        {
            "content": "BLOCK NameSystem addStoredBlock blockMap updated for blk_7503483334202473044",
            "component": "dfs.FSNamesystem",
            "level": "INFO",
            "block_id": "blk_7503483334202473044",
            "anomaly": 0,
        },
        {
            "content": "Error receiving block blk_-3544583377289625738 bad packet checksum detected",
            "component": "dfs.DataNode$DataXceiver",
            "level": "ERROR",
            "block_id": "blk_-3544583377289625738",
            "anomaly": 1,
        },
        {
            "content": "Block blk_-3544583377289625738 marked corrupt due to replica mismatch",
            "component": "dfs.FSNamesystem",
            "level": "WARN",
            "block_id": "blk_-3544583377289625738",
            "anomaly": 1,
        },
        {
            "content": "Received exception while serving block blk_112233445566 broken pipe",
            "component": "dfs.DataNode$DataXceiver",
            "level": "ERROR",
            "block_id": "blk_112233445566",
            "anomaly": 1,
        },
        {
            "content": "Verification succeeded for block blk_998877665544 on DataNode",
            "component": "dfs.DataNode$BlockReceiver",
            "level": "INFO",
            "block_id": "blk_998877665544",
            "anomaly": 0,
        },
        {
            "content": "Replicating block blk_998877665544 to target node completed",
            "component": "dfs.DataNode$DataTransfer",
            "level": "INFO",
            "block_id": "blk_998877665544",
            "anomaly": 0,
        },
        {
            "content": "Failed to replicate block blk_223344556677 no live nodes contain current replica",
            "component": "dfs.FSNamesystem",
            "level": "ERROR",
            "block_id": "blk_223344556677",
            "anomaly": 1,
        },
        {
            "content": "Served block blk_223344556678 to client /10.251.30.134",
            "component": "dfs.DataNode$DataXceiver",
            "level": "INFO",
            "block_id": "blk_223344556678",
            "anomaly": 0,
        },
        {
            "content": "Could not obtain block length for blk_223344556677 due to missing metadata",
            "component": "dfs.DataNode$FSDataset",
            "level": "WARN",
            "block_id": "blk_223344556677",
            "anomaly": 1,
        },
        {
            "content": "Block report from node 10.251.111.209 processed successfully",
            "component": "dfs.FSNamesystem",
            "level": "INFO",
            "block_id": "blk_556677889900",
            "anomaly": 0,
        },
    ]
    return pd.DataFrame(rows)
