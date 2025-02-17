from typing import Dict, List, Optional, Tuple
import time
import json
from collections import defaultdict
import numpy as np
from datetime import datetime

class EnhancedContextManager:
    def __init__(self, max_context_size: int = 1000):
        # Main context storage
        self.context_store: Dict[str, Dict] = {}
        
        # Hierarchical relationship storage
        self.context_hierarchy: Dict[str, List[str]] = defaultdict(list)
        
        # Inverse hierarchy for quick parent lookup
        self.parent_lookup: Dict[str, str] = {}
        
        # Context metadata storage
        self.context_metadata: Dict[str, Dict] = {}
        
        # Relevance scoring history
        self.relevance_history: Dict[str, List[float]] = defaultdict(list)
        
        # Configuration
        self.max_context_size = max_context_size
        self.relevance_threshold = 0.3
        self.max_context_age = 3600  # 1 hour in seconds
        
    def preserve_context(self, context_id: str, context_data: dict, 
                        parent_id: Optional[str] = None, 
                        metadata: Optional[dict] = None) -> Tuple[bool, str]:
        """
        Preserves context with hierarchical relationships and metadata
        
        Args:
            context_id: Unique identifier for the context
            context_data: The context data to preserve
            parent_id: Optional parent context ID for hierarchy
            metadata: Optional metadata about the context
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate input
            if not context_id or not isinstance(context_data, dict):
                return False, "Invalid context_id or context_data"
                
            # Check for context size limits
            if len(self.context_store) >= self.max_context_size:
                self._cleanup_old_contexts()
                
            # Prepare context metadata
            current_time = time.time()
            context_metadata = {
                "created_at": current_time,
                "last_accessed": current_time,
                "access_count": 0,
                "importance_score": self._calculate_importance(context_data),
                "tags": metadata.get("tags", []) if metadata else [],
                "source": metadata.get("source", "unknown") if metadata else "unknown",
                "version": metadata.get("version", "1.0") if metadata else "1.0"
            }
            
            # Store context and metadata
            self.context_store[context_id] = self._preprocess_context(context_data)
            self.context_metadata[context_id] = context_metadata
            
            # Handle hierarchical relationship
            if parent_id and parent_id in self.context_store:
                self.context_hierarchy[parent_id].append(context_id)
                self.parent_lookup[context_id] = parent_id
                
            return True, "Context preserved successfully"
            
        except Exception as e:
            return False, f"Error preserving context: {str(e)}"
            
    def retrieve_context(self, context_id: str, 
                        include_children: bool = False,
                        include_relevance: bool = True) -> Tuple[Optional[Dict], float]:
        """
        Retrieves context with optional hierarchy and relevance scoring
        
        Args:
            context_id: The ID of the context to retrieve
            include_children: Whether to include child contexts
            include_relevance: Whether to calculate relevance score
            
        Returns:
            Tuple of (context_data: Optional[Dict], relevance_score: float)
        """
        try:
            if context_id not in self.context_store:
                return None, 0.0
                
            # Update access metadata
            self._update_access_metadata(context_id)
            
            # Get base context
            context_data = self.context_store[context_id]
            
            # Include child contexts if requested
            if include_children:
                children = self.get_child_contexts(context_id)
                if children:
                    context_data = {
                        "main_context": context_data,
                        "child_contexts": children
                    }
                    
            # Calculate relevance score
            relevance_score = (
                self._calculate_relevance(context_id) if include_relevance else 1.0
            )
            
            return context_data, relevance_score
            
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return None, 0.0
            
    def update_context(self, context_id: str, 
                      updates: dict,
                      merge: bool = True) -> Tuple[bool, str]:
        """
        Updates existing context with new data
        
        Args:
            context_id: The ID of the context to update
            updates: The updates to apply
            merge: Whether to merge with existing data or replace
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if context_id not in self.context_store:
                return False, "Context not found"
                
            if merge:
                current_context = self.context_store[context_id]
                self.context_store[context_id] = self._deep_merge(
                    current_context, updates
                )
            else:
                self.context_store[context_id] = updates
                
            # Update metadata
            self.context_metadata[context_id]["last_accessed"] = time.time()
            self.context_metadata[context_id]["version"] = str(
                float(self.context_metadata[context_id]["version"]) + 0.1
            )
            
            return True, "Context updated successfully"
            
        except Exception as e:
            return False, f"Error updating context: {str(e)}"
            
    def get_child_contexts(self, context_id: str) -> Optional[Dict[str, Dict]]:
        """
        Retrieves all child contexts for a given context ID
        """
        if context_id not in self.context_hierarchy:
            return None
            
        children = {}
        for child_id in self.context_hierarchy[context_id]:
            child_data, _ = self.retrieve_context(child_id, include_children=False)
            if child_data:
                children[child_id] = child_data
                
        return children
        
    def get_context_chain(self, context_id: str) -> List[Dict]:
        """
        Retrieves the full chain of parent contexts
        """
        chain = []
        current_id = context_id
        
        while current_id in self.parent_lookup:
            parent_id = self.parent_lookup[current_id]
            parent_data, _ = self.retrieve_context(parent_id, include_children=False)
            if parent_data:
                chain.append({
                    "context_id": parent_id,
                    "data": parent_data
                })
            current_id = parent_id
            
        return chain
        
    def _calculate_importance(self, context_data: dict) -> float:
        """
        Calculates importance score based on context complexity and content
        """
        # Factor in data size
        size_score = min(len(json.dumps(context_data)) / 1000, 1.0)
        
        # Factor in data complexity
        complexity_score = len(str(context_data).split()) / 100
        
        # Factor in hierarchical position
        hierarchy_score = 0.5
        
        return (size_score + complexity_score + hierarchy_score) / 3
        
    def _calculate_relevance(self, context_id: str) -> float:
        """
        Calculates relevance score based on recency, access patterns, and importance
        """
        metadata = self.context_metadata[context_id]
        current_time = time.time()
        
        # Time decay factor
        time_factor = np.exp(
            -(current_time - metadata["last_accessed"]) / self.max_context_age
        )
        
        # Access frequency factor
        access_factor = min(metadata["access_count"] / 100, 1.0)
        
        # Importance factor
        importance_factor = metadata["importance_score"]
        
        # Combined relevance score
        relevance = (time_factor * 0.4 + access_factor * 0.3 + importance_factor * 0.3)
        
        # Update relevance history
        self.relevance_history[context_id].append(relevance)
        if len(self.relevance_history[context_id]) > 10:
            self.relevance_history[context_id].pop(0)
            
        return relevance
        
    def _cleanup_old_contexts(self):
        """
        Removes old or irrelevant contexts to maintain size limits
        """
        current_time = time.time()
        contexts_to_remove = []
        
        for context_id, metadata in self.context_metadata.items():
            # Remove if too old
            if current_time - metadata["last_accessed"] > self.max_context_age:
                contexts_to_remove.append(context_id)
                continue
                
            # Remove if relevance is too low
            relevance = self._calculate_relevance(context_id)
            if relevance < self.relevance_threshold:
                contexts_to_remove.append(context_id)
                
        # Perform removal
        for context_id in contexts_to_remove:
            self._remove_context(context_id)
            
    def _remove_context(self, context_id: str):
        """
        Safely removes a context and its references
        """
        # Remove from main storage
        self.context_store.pop(context_id, None)
        self.context_metadata.pop(context_id, None)
        
        # Remove from hierarchy
        if context_id in self.context_hierarchy:
            for child_id in self.context_hierarchy[context_id]:
                self.parent_lookup.pop(child_id, None)
            self.context_hierarchy.pop(context_id)
            
        # Remove from parent lookup
        self.parent_lookup.pop(context_id, None)
        
        # Remove from relevance history
        self.relevance_history.pop(context_id, None)
        
    def _update_access_metadata(self, context_id: str):
        """
        Updates metadata when context is accessed
        """
        if context_id in self.context_metadata:
            self.context_metadata[context_id]["last_accessed"] = time.time()
            self.context_metadata[context_id]["access_count"] += 1
            
    def _preprocess_context(self, context_data: dict) -> dict:
        """
        Preprocesses context data before storage
        """
        # Convert datetime objects to timestamps
        return json.loads(json.dumps(context_data, default=str))
        
    def _deep_merge(self, dict1: dict, dict2: dict) -> dict:
        """
        Deeply merges two dictionaries
        """
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
