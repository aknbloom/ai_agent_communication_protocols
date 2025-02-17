from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re
import json

class VersionChangeType(Enum):
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    PATCH = "PATCH"

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    
    @staticmethod
    def parse(version_str: str) -> 'Version':
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return Version(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3))
        )
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other: 'Version') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

class ProtocolVersionManager:
    def __init__(self):
        # Supported protocol versions
        self.supported_versions: List[str] = [
            "1.0.0", "1.1.0", "2.0.0", "2.1.0", "2.1.1"
        ]
        
        # Compatibility matrix
        self.backwards_compatibility: Dict[str, List[str]] = {
            "2.1.1": ["2.1.0", "2.0.0"],
            "2.1.0": ["2.0.0"],
            "2.0.0": ["1.1.0", "1.0.0"],
            "1.1.0": ["1.0.0"],
            "1.0.0": []
        }
        
        # Protocol features by version
        self.version_features: Dict[str, Dict] = {
            "2.1.1": {
                "encryption": ["AES-256", "RSA-4096"],
                "compression": ["gzip", "zlib"],
                "authentication": ["JWT", "OAuth2"],
                "streaming": True
            },
            "2.0.0": {
                "encryption": ["AES-256"],
                "compression": ["gzip"],
                "authentication": ["JWT"],
                "streaming": False
            },
            "1.0.0": {
                "encryption": ["AES-128"],
                "compression": None,
                "authentication": ["Basic"],
                "streaming": False
            }
        }
        
        # Schema registry
        self.schema_registry: Dict[str, Dict] = {}
        
    def negotiate_version(self, agent1_version: str, 
                         agent2_version: str,
                         required_features: Optional[List[str]] = None) -> Tuple[str, Dict]:
        """
        Negotiates the highest compatible version between two agents
        
        Args:
            agent1_version: Version supported by first agent
            agent2_version: Version supported by second agent
            required_features: Optional list of required features
            
        Returns:
            Tuple of (negotiated_version, feature_set)
        """
        try:
            # Parse versions
            v1 = Version.parse(agent1_version)
            v2 = Version.parse(agent2_version)
            
            # Get all compatible versions
            compatible_versions = self._get_compatible_versions(str(v1), str(v2))
            
            if not compatible_versions:
                raise ValueError(f"No compatible versions between {v1} and {v2}")
                
            # Filter by required features if specified
            if required_features:
                compatible_versions = [
                    v for v in compatible_versions
                    if self._supports_features(v, required_features)
                ]
                
                if not compatible_versions:
                    raise ValueError("No versions support required features")
                    
            # Select highest compatible version
            negotiated_version = max(compatible_versions, key=Version.parse)
            
            # Get feature set for negotiated version
            feature_set = self.version_features.get(negotiated_version, {})
            
            return negotiated_version, feature_set
            
        except Exception as e:
            raise ValueError(f"Version negotiation failed: {str(e)}")
            
    def validate_upgrade(self, old_version: str, 
                        new_version: str,
                        schema_changes: Dict) -> Tuple[bool, str, VersionChangeType]:
        """
        Validates if an upgrade between versions is safe
        
        Args:
            old_version: Current version
            new_version: Target version
            schema_changes: Proposed schema changes
            
        Returns:
            Tuple of (is_valid, message, change_type)
        """
        try:
            old_v = Version.parse(old_version)
            new_v = Version.parse(new_version)
            
            if new_v < old_v:
                return False, "New version cannot be lower than old version", None
                
            # Analyze schema changes
            change_type = self._analyze_schema_changes(schema_changes)
            
            # Validate version increment matches change type
            if not self._validate_version_increment(old_v, new_v, change_type):
                return False, f"Version increment doesn't match change type: {change_type}", change_type
                
            # Register new schema version
            self.schema_registry[new_version] = schema_changes
            
            return True, "Version upgrade is valid", change_type
            
        except Exception as e:
            return False, f"Validation failed: {str(e)}", None
            
    def _get_compatible_versions(self, version1: str, version2: str) -> List[str]:
        """
        Gets all versions compatible with both input versions
        """
        v1_compatible = set([version1] + self._get_backward_compatible_versions(version1))
        v2_compatible = set([version2] + self._get_backward_compatible_versions(version2))
        
        return sorted(list(v1_compatible.intersection(v2_compatible)))
        
    def _get_backward_compatible_versions(self, version: str) -> List[str]:
        """
        Gets all versions backward compatible with input version
        """
        compatible_versions = []
        current_version = version
        
        while current_version in self.backwards_compatibility:
            compatible_versions.extend(self.backwards_compatibility[current_version])
            if not self.backwards_compatibility[current_version]:
                break
            current_version = self.backwards_compatibility[current_version][0]
            
        return compatible_versions
        
    def _supports_features(self, version: str, required_features: List[str]) -> bool:
        """
        Checks if version supports all required features
        """
        if version not in self.version_features:
            return False
            
        version_features = self.version_features[version]
        return all(
            feature in version_features and version_features[feature]
            for feature in required_features
        )
        
    def _analyze_schema_changes(self, changes: Dict) -> VersionChangeType:
        """
        Analyzes schema changes to determine change type
        """
        has_breaking = False
        has_new_features = False
        
        for change_type, changes_list in changes.items():
            if change_type == "breaking_changes" and changes_list:
                has_breaking = True
            elif change_type == "new_features" and changes_list:
                has_new_features = True
                
        if has_breaking:
            return VersionChangeType.MAJOR
        elif has_new_features:
            return VersionChangeType.MINOR
        return VersionChangeType.PATCH
        
    def _validate_version_increment(self, old_v: Version, 
                                  new_v: Version,
                                  change_type: VersionChangeType) -> bool:
        """
        Validates version increment matches change type
        """
        if change_type == VersionChangeType.MAJOR:
            return new_v.major == old_v.major + 1
        elif change_type == VersionChangeType.MINOR:
            return new_v.major == old_v.major and new_v.minor == old_v.minor + 1
        elif change_type == VersionChangeType.PATCH:
            return (new_v.major == old_v.major and 
                   new_v.minor == old_v.minor and 
                   new_v.patch == old_v.patch + 1)
        return False

# Usage Example
def example_usage():
    version_manager = ProtocolVersionManager()
    
    # Negotiate version between agents
    agent1_version = "2.1.0"
    agent2_version = "1.1.0"
    required_features = ["encryption"]
    
    try:
        negotiated_version, features = version_manager.negotiate_version(
            agent1_version,
            agent2_version,
            required_features
        )
        print(f"Negotiated Version: {negotiated_version}")
        print(f"Available Features: {features}")
        
        # Validate version upgrade
        schema_changes = {
            "breaking_changes": ["removed_field_x"],
            "new_features": ["added_field_y"],
            "bug_fixes": ["fixed_validation"]
        }
        
        is_valid, message, change_type = version_manager.validate_upgrade(
            "1.0.0",
            "2.0.0",
            schema_changes
        )
        print(f"Upgrade Valid: {is_valid}")
        print(f"Message: {message}")
        print(f"Change Type: {change_type}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    example_usage()
