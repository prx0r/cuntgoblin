"""TaskSpec taxonomy for VentureLab factory."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskType:
    """A task type in the taxonomy."""
    name: str
    description: str
    quality_floor: float
    free_policy: str
    tools_required: bool
    criticality: str


# Task taxonomy
TASK_TAXONOMY = {
    # Research tasks
    "source_extract": TaskType(
        name="source_extract",
        description="Extract data from sources",
        quality_floor=0.55,
        free_policy="prefer",
        tools_required=False,
        criticality="routine",
    ),
    "source_analysis": TaskType(
        name="source_analysis",
        description="Analyze extracted data",
        quality_floor=0.62,
        free_policy="prefer",
        tools_required=False,
        criticality="routine",
    ),
    "research_synthesis": TaskType(
        name="research_synthesis",
        description="Synthesize research findings",
        quality_floor=0.70,
        free_policy="prefer",
        tools_required=False,
        criticality="routine",
    ),
    
    # Solution tasks
    "solution_generation": TaskType(
        name="solution_generation",
        description="Generate solution hypotheses",
        quality_floor=0.65,
        free_policy="prefer",
        tools_required=False,
        criticality="routine",
    ),
    "architecture_design": TaskType(
        name="architecture_design",
        description="Design system architecture",
        quality_floor=0.78,
        free_policy="paid_allowed",
        tools_required=True,
        criticality="important",
    ),
    "specification": TaskType(
        name="specification",
        description="Write technical specifications",
        quality_floor=0.80,
        free_policy="paid_allowed",
        tools_required=True,
        criticality="important",
    ),
    
    # Coding tasks
    "coding_scaffold": TaskType(
        name="coding_scaffold",
        description="Generate code scaffold",
        quality_floor=0.65,
        free_policy="prefer",
        tools_required=True,
        criticality="routine",
    ),
    "coding_patch": TaskType(
        name="coding_patch",
        description="Apply code patch",
        quality_floor=0.76,
        free_policy="prefer",
        tools_required=True,
        criticality="routine",
    ),
    "coding_feature": TaskType(
        name="coding_feature",
        description="Implement new feature",
        quality_floor=0.80,
        free_policy="paid_allowed",
        tools_required=True,
        criticality="important",
    ),
    "debugging": TaskType(
        name="debugging",
        description="Debug code issues",
        quality_floor=0.78,
        free_policy="prefer",
        tools_required=True,
        criticality="routine",
    ),
    
    # Review tasks
    "code_review": TaskType(
        name="code_review",
        description="Review code quality",
        quality_floor=0.82,
        free_policy="paid_allowed",
        tools_required=True,
        criticality="important",
    ),
    "certification": TaskType(
        name="certification",
        description="Certify production readiness",
        quality_floor=0.88,
        free_policy="no_exploration",
        tools_required=True,
        criticality="release_gate",
    ),
    "security_review": TaskType(
        name="security_review",
        description="Security review",
        quality_floor=0.90,
        free_policy="no_exploration",
        tools_required=True,
        criticality="release_gate",
    ),
    "release_finish": TaskType(
        name="release_finish",
        description="Final release preparation",
        quality_floor=0.90,
        free_policy="no_exploration",
        tools_required=True,
        criticality="release_gate",
    ),
}


def get_task_type(name: str) -> Optional[TaskType]:
    """Get task type by name."""
    return TASK_TAXONOMY.get(name)


def list_task_types() -> list:
    """List all task types."""
    return list(TASK_TAXONOMY.values())


def test_taxonomy():
    """Test the taxonomy."""
    print("=== TASK TAXONOMY ===")
    print()
    
    for name, task in TASK_TAXONOMY.items():
        print(f"{name}:")
        print(f"  Description: {task.description}")
        print(f"  Quality floor: {task.quality_floor}")
        print(f"  Free policy: {task.free_policy}")
        print(f"  Tools required: {task.tools_required}")
        print(f"  Criticality: {task.criticality}")
        print()
    
    print("=== TEST PASSED ===")


if __name__ == "__main__":
    test_taxonomy()
