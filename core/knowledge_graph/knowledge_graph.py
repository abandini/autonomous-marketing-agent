"""
Knowledge Graph module for the Autonomous Marketing Agent.

This module implements the central knowledge graph that maintains information
about websites, industry, competitors, and marketing performance.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
import networkx as nx
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketingKnowledgeGraph:
    """
    Knowledge Graph for marketing data and relationships.
    
    The knowledge graph maintains information about:
    1. Website content and structure
    2. Industry and competitors
    3. Marketing campaigns and performance
    4. Customer segments and behaviors
    5. Content topics and keywords
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Marketing Knowledge Graph.
        
        Args:
            config: Configuration for the knowledge graph
        """
        self.config = config
        self.graph = nx.MultiDiGraph()
        self.persistence_path = config.get("persistence_path", "data/knowledge_graph")
        self.last_updated = datetime.now()
        
        # Initialize graph with base node types
        self._initialize_base_nodes()
        
        # Load existing data if available
        if config.get("load_on_init", True):
            self.load()
            
        logger.info("Marketing Knowledge Graph initialized")
        
    def _initialize_base_nodes(self) -> None:
        """
        Initialize the graph with base node types.
        """
        base_nodes = [
            {"id": "root", "type": "root", "name": "Marketing Knowledge Graph"},
            {"id": "websites", "type": "category", "name": "Websites"},
            {"id": "competitors", "type": "category", "name": "Competitors"},
            {"id": "campaigns", "type": "category", "name": "Marketing Campaigns"},
            {"id": "content", "type": "category", "name": "Content"},
            {"id": "channels", "type": "category", "name": "Marketing Channels"},
            {"id": "audiences", "type": "category", "name": "Target Audiences"},
            {"id": "keywords", "type": "category", "name": "Keywords"},
            {"id": "metrics", "type": "category", "name": "Performance Metrics"}
        ]
        
        for node in base_nodes:
            self.add_node(node["id"], node)
            
            if node["id"] != "root":
                self.add_edge("root", node["id"], {"type": "contains"})
                
        logger.debug("Initialized base nodes in knowledge graph")
        
    def add_node(self, node_id: str, attributes: Dict[str, Any]) -> bool:
        """
        Add a node to the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node
            attributes: Attributes for the node
            
        Returns:
            True if the node was added, False otherwise
        """
        try:
            # Add created_at and updated_at timestamps
            if "created_at" not in attributes:
                attributes["created_at"] = datetime.now().isoformat()
                
            attributes["updated_at"] = datetime.now().isoformat()
            
            self.graph.add_node(node_id, **attributes)
            self.last_updated = datetime.now()
            logger.debug(f"Added node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {str(e)}")
            return False
            
    def update_node(self, node_id: str, attributes: Dict[str, Any]) -> bool:
        """
        Update a node in the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node
            attributes: Updated attributes for the node
            
        Returns:
            True if the node was updated, False otherwise
        """
        if node_id not in self.graph:
            logger.error(f"Node {node_id} not found")
            return False
            
        try:
            # Update the attributes
            current_attrs = self.graph.nodes[node_id]
            
            # Update updated_at timestamp
            attributes["updated_at"] = datetime.now().isoformat()
            
            # Merge attributes
            for key, value in attributes.items():
                current_attrs[key] = value
                
            self.last_updated = datetime.now()
            logger.debug(f"Updated node: {node_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update node {node_id}: {str(e)}")
            return False
            
    def add_edge(self, source_id: str, target_id: str, attributes: Dict[str, Any]) -> bool:
        """
        Add an edge between two nodes in the knowledge graph.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            attributes: Attributes for the edge
            
        Returns:
            True if the edge was added, False otherwise
        """
        if source_id not in self.graph:
            logger.error(f"Source node {source_id} not found")
            return False
            
        if target_id not in self.graph:
            logger.error(f"Target node {target_id} not found")
            return False
            
        try:
            # Add created_at and updated_at timestamps
            if "created_at" not in attributes:
                attributes["created_at"] = datetime.now().isoformat()
                
            attributes["updated_at"] = datetime.now().isoformat()
            
            self.graph.add_edge(source_id, target_id, **attributes)
            self.last_updated = datetime.now()
            logger.debug(f"Added edge: {source_id} -> {target_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add edge {source_id} -> {target_id}: {str(e)}")
            return False
            
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node from the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            Dict containing node attributes, or None if not found
        """
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        else:
            logger.debug(f"Node not found: {node_id}")
            return None
            
    def has_node(self, node_id: str) -> bool:
        """
        Check if a node exists in the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node
            
        Returns:
            True if the node exists, False otherwise
        """
        return node_id in self.graph.nodes
        
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get neighbors of a node in the knowledge graph.
        
        Args:
            node_id: Unique identifier for the node
            edge_type: Optional filter for edge type
            
        Returns:
            List of neighbor nodes
        """
        if node_id not in self.graph:
            logger.error(f"Node {node_id} not found")
            return []
            
        neighbors = []
        
        for _, neighbor_id, edge_data in self.graph.out_edges(node_id, data=True):
            if edge_type is None or edge_data.get("type") == edge_type:
                neighbor_data = dict(self.graph.nodes[neighbor_id])
                neighbor_data["edge"] = edge_data
                neighbors.append(neighbor_data)
                
        return neighbors
        
    def query(self, node_type: Optional[str] = None, attributes: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Query nodes in the knowledge graph.
        
        Args:
            node_type: Optional filter for node type
            attributes: Optional filter for node attributes
            
        Returns:
            List of nodes matching the query
        """
        results = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            # Check node type
            if node_type is not None and node_data.get("type") != node_type:
                continue
                
            # Check attributes
            if attributes is not None:
                match = True
                
                for key, value in attributes.items():
                    if key not in node_data or node_data[key] != value:
                        match = False
                        break
                        
                if not match:
                    continue
                    
            # Add to results
            node_result = dict(node_data)
            node_result["id"] = node_id
            results.append(node_result)
            
        return results
        
    def save(self, path: Optional[str] = None) -> bool:
        """
        Save the knowledge graph to disk.
        
        Args:
            path: Optional path to save the graph
            
        Returns:
            True if the graph was saved, False otherwise
        """
        save_path = path or self.persistence_path
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Convert graph to JSON
            data = nx.node_link_data(self.graph)
            
            # Save to file
            with open(save_path, 'w') as file:
                json.dump(data, file)
                
            logger.info(f"Knowledge graph saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {str(e)}")
            return False
            
    def load(self, path: Optional[str] = None) -> bool:
        """
        Load the knowledge graph from disk.
        
        Args:
            path: Optional path to load the graph from
            
        Returns:
            True if the graph was loaded, False otherwise
        """
        load_path = path or self.persistence_path
        
        if not os.path.exists(load_path):
            logger.warning(f"Knowledge graph file not found at {load_path}")
            return False
            
        try:
            # Load from file
            with open(load_path, 'r') as file:
                data = json.load(file)
                
            # Convert JSON to graph
            self.graph = nx.node_link_graph(data)
            
            logger.info(f"Knowledge graph loaded from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {str(e)}")
            return False
            
    def get_subgraph(self, node_ids: List[str]) -> nx.MultiDiGraph:
        """
        Get a subgraph containing only the specified nodes.
        
        Args:
            node_ids: List of node IDs to include in the subgraph
            
        Returns:
            Subgraph containing only the specified nodes
        """
        return self.graph.subgraph(node_ids)
        
    def export_to_dataframe(self, node_type: Optional[str] = None) -> pd.DataFrame:
        """
        Export nodes to a pandas DataFrame.
        
        Args:
            node_type: Optional filter for node type
            
        Returns:
            DataFrame containing node data
        """
        nodes = self.query(node_type=node_type)
        return pd.DataFrame(nodes)
        
    def get_nodes_by_attribute(self, attribute: str, value: Any) -> Dict[str, Dict[str, Any]]:
        """
        Get nodes that have a specific attribute value.
        
        Args:
            attribute: The attribute name to match
            value: The attribute value to match
            
        Returns:
            Dictionary of node_id -> node_attributes for matching nodes
        """
        matching_nodes = {}
        
        for node_id, node_data in self.graph.nodes(data=True):
            if attribute in node_data and node_data[attribute] == value:
                matching_nodes[node_id] = dict(node_data)
                
        return matching_nodes
        
    def get_connected_nodes(self, node_id: str, edge_type: Optional[str] = None, direction: str = "both") -> Dict[str, Dict[str, Any]]:
        """
        Get nodes connected to the specified node.
        
        Args:
            node_id: ID of the node to get connections for
            edge_type: Optional filter for edge type
            direction: Direction of edges to consider ('incoming', 'outgoing', or 'both')
            
        Returns:
            Dictionary of node_id -> node_attributes for connected nodes
        """
        if node_id not in self.graph:
            logger.error(f"Node {node_id} not found")
            return {}
            
        connected_nodes = {}
        
        # Get outgoing edges
        if direction in ["outgoing", "both"]:
            for _, target_id, edge_data in self.graph.out_edges(node_id, data=True):
                if edge_type is None or edge_data.get("type") == edge_type:
                    connected_nodes[target_id] = dict(self.graph.nodes[target_id])
        
        # Get incoming edges
        if direction in ["incoming", "both"]:
            for source_id, _, edge_data in self.graph.in_edges(node_id, data=True):
                if edge_type is None or edge_data.get("type") == edge_type:
                    connected_nodes[source_id] = dict(self.graph.nodes[source_id])
                    
        return connected_nodes
        
    def import_from_dataframe(self, df: pd.DataFrame, node_type: str, id_column: str) -> int:
        """
        Import nodes from a pandas DataFrame.
        
        Args:
            df: DataFrame containing node data
            node_type: Type for the imported nodes
            id_column: Column to use as node ID
            
        Returns:
            Number of nodes imported
        """
        count = 0
        
        for _, row in df.iterrows():
            node_id = str(row[id_column])
            
            # Convert row to dict
            attributes = row.to_dict()
            attributes["type"] = node_type
            
            # Remove ID column from attributes
            if id_column in attributes:
                del attributes[id_column]
                
            # Add node
            if self.add_node(node_id, attributes):
                count += 1
                
        logger.info(f"Imported {count} nodes of type {node_type}")
        return count
        
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dict containing graph statistics
        """
        node_types = {}
        edge_types = {}
        
        # Count node types
        for _, node_data in self.graph.nodes(data=True):
            node_type = node_data.get("type", "unknown")
            
            if node_type not in node_types:
                node_types[node_type] = 0
                
            node_types[node_type] += 1
            
        # Count edge types
        for _, _, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get("type", "unknown")
            
            if edge_type not in edge_types:
                edge_types[edge_type] = 0
                
            edge_types[edge_type] += 1
            
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "node_types": node_types,
            "edge_types": edge_types,
            "last_updated": self.last_updated.isoformat()
        }
