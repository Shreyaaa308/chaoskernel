import io
import base64

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

def generate_blast_radius_chart(chaos_payload):
    """
    Generate a blast-radius chart from ChaosKernel analysis data.

    Args:
        chaos_payload (dict): Contains service details and component statuses.

    Returns:
        str: Base64-encoded PNG image.
    """
        # Check whether the input is a valid dictionary
    if not isinstance(chaos_payload, dict):
        raise TypeError("chaos_payload must be a dictionary")

    # Extract the component health information
    components = chaos_payload.get("blast_radius_nodes")

    if not isinstance(components, dict) or not components:
        raise ValueError("No valid component information provided")

    # Extract general information about the failure
    target_service = chaos_payload.get("target_service", "Unknown Service")
    threat_type = chaos_payload.get("threat_type", "Unknown Threat")
    severity = chaos_payload.get("severity", "Unknown Severity")
        # Assign a colour to each component status
    status_colors = {
        "HEALTHY": "green",
        "DEGRADED": "orange",
        "FAILED": "red"
    }

    # Extract component names and their statuses
    component_names = list(components.keys())
    component_statuses = [str(status).upper() for status in components.values()]

    # Match each component with its corresponding colour
    component_colors = [
        status_colors.get(status, "gray")
        for status in component_statuses
    ]
        # Create the chart
    fig, ax = plt.subplots(figsize=(10, 5))

    # Draw a horizontal bar for each component
    bars = ax.barh(
        component_names,
        [1] * len(component_names),
        color=component_colors,
        height=0.6
    )

    # Display each component's health status
    for bar, status in zip(bars, component_statuses):
        ax.text(
            bar.get_width() / 2,
            bar.get_y() + bar.get_height() / 2,
            status,
            ha="center",
            va="center",
            color="white",
            fontweight="bold"
        )

    # Display components from top to bottom
    ax.invert_yaxis()
        # Add chart title and failure information
    ax.set_title(
        f"ChaosKernel Blast Radius: {target_service}\n"
        f"Threat: {threat_type} | Severity: {severity}",
        fontsize=12,
        fontweight="bold",
        pad=20
    )

    # Label the chart
    ax.set_xlabel("Component Health Status")
    ax.set_ylabel("Affected Components")

    # Remove unnecessary chart borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Adjust spacing to prevent text from being cut off
    plt.tight_layout()
        # Create an in-memory buffer to store the PNG image
    image_buffer = io.BytesIO()

    # Save the chart as a PNG image inside the buffer
    fig.savefig(
        image_buffer,
        format="png",
        dpi=150,
        bbox_inches="tight"
    )

    # Move to the beginning of the image buffer
    image_buffer.seek(0)

    # Convert the PNG image into a Base64 string
    image_base64 = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    # Close the buffer and chart to free memory
    image_buffer.close()
    plt.close(fig)

    # Return the Base64 image
    return image_base64

