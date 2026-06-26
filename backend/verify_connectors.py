import sys
import time
from connectors.sync.sync_engine import sync_engine_instance
from organization.models.org_graph import org_graph_instance

def run_tests():
    print("====================================")
    print("Verifying Connector Registry Operations")
    print("====================================")
    
    # 1. Check connectors list
    conns = sync_engine_instance.get_connectors_info()
    print(f"Total Connectors: {len(conns)}")
    assert len(conns) == 8, "Expected 8 mock connectors"
    
    github_info = next(c for c in conns if c["provider"] == "GitHub")
    print(f"GitHub Status: Connected = {github_info['connected']}")
    assert github_info['connected'] == False, "GitHub should start disconnected"
    print("[OK] Connectors registry listing check passed.")

    # 2. Connect GitHub
    print("\n====================================")
    print("Connecting GitHub Provider")
    print("====================================")
    success = sync_engine_instance.connect_provider("GitHub", {"token": "ghp_mock_token"})
    assert success == True, "Failed to connect GitHub"
    
    conns = sync_engine_instance.get_connectors_info()
    github_info = next(c for c in conns if c["provider"] == "GitHub")
    print(f"GitHub Status: Connected = {github_info['connected']}")
    assert github_info['connected'] == True, "GitHub should now be connected"
    print("[OK] Connect provider passed.")

    # 3. Perform Sync Ingestion
    print("\n====================================")
    print("Performing GitHub Full Sync (Graph Ingestion)")
    print("====================================")
    
    # Initial graph check
    init_nodes_count = len(org_graph_instance.serialize()["nodes"])
    print(f"Initial Org Graph nodes: {init_nodes_count}")
    
    result = sync_engine_instance.sync_provider("GitHub", "full")
    print(f"Sync Result: {result}")
    assert result["success"] == True, "Sync failed"
    assert result["items_synced"] == 6, "Expected 6 mock items synced"
    
    # Post graph check
    post_nodes = org_graph_instance.serialize()["nodes"]
    post_nodes_count = len(post_nodes)
    print(f"Post-Sync Org Graph nodes: {post_nodes_count}")
    assert post_nodes_count > init_nodes_count, "No nodes were ingested into the graph"
    
    # Check that Gary and Repo_Next_App are present in the graph
    gary_node = org_graph_instance.find_node("Gary")
    print(f"Discovered Person Node 'Gary': {gary_node}")
    assert gary_node is not None, "Gary should be added to the graph"
    assert gary_node["properties"]["data_source"] == "GitHub", "Ingestion origin metadata missing"
    
    repo_node = org_graph_instance.find_node("Repo_Next_App")
    print(f"Discovered Repository Node 'Repo_Next_App': {repo_node}")
    assert repo_node is not None, "Repo_Next_App should be added to the graph"
    
    print("[OK] Ingestion into Knowledge Graph passed.")

    # 4. Perform Incremental Sync
    print("\n====================================")
    print("Performing GitHub Incremental Sync")
    print("====================================")
    # Perform second sync (incremental mode)
    inc_result = sync_engine_instance.sync_provider("GitHub", "incremental")
    print(f"Incremental Sync Result: {inc_result}")
    assert inc_result["success"] == True, "Incremental sync failed"
    # In mock, since timestamps are not updated, incremental should return 0 items newer than last sync
    print(f"Items synced during incremental: {inc_result['items_synced']}")
    
    # 5. Check Status and History
    print("\n====================================")
    print("Verifying Status & History API data")
    print("====================================")
    status = sync_engine_instance.get_status()
    print(f"System Health Status: {status}")
    assert status["connected_count"] == 1, "Expected 1 connected provider"
    
    history = sync_engine_instance.sync_history
    print(f"Total Sync History Logs: {len(history)}")
    assert len(history) == 2, "Expected 2 sync execution logs"
    print("[OK] Status & History check passed.")

    # 6. Disconnect Provider
    print("\n====================================")
    print("Disconnecting GitHub Provider")
    print("====================================")
    disc_success = sync_engine_instance.disconnect_provider("GitHub")
    assert disc_success == True
    
    conns = sync_engine_instance.get_connectors_info()
    github_info = next(c for c in conns if c["provider"] == "GitHub")
    assert github_info['connected'] == False, "GitHub should be disconnected"
    print("[OK] Disconnect provider passed.")

    print("\nALL CONNECTOR FRAMEWORK TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
