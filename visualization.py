import streamlit as st
import base64
from io import BytesIO
import pandas as pd

def create_score_gauge(score, width=200, height=120):
    """
    Create an HTML/CSS gauge for displaying a score from 0-100.
    
    Args:
        score (float): Score value (0-100)
        width (int): Width of the gauge in pixels
        height (int): Height of the gauge in pixels
        
    Returns:
        str: HTML for the gauge
    """
    # Determine color based on score
    if score >= 80:
        color = "#28a745"  # Green
    elif score >= 60:
        color = "#ffc107"  # Yellow
    else:
        color = "#dc3545"  # Red
    
    # Calculate rotation angle (0-180 degrees)
    angle = score * 1.8  # Convert 0-100 to 0-180 degrees
    
    # Create HTML with inline CSS for the gauge
    html = f"""
    <div style="width:{width}px; margin:0 auto;">
        <div style="text-align:center; font-size:20px; font-weight:bold; margin-bottom:5px;">
            {score}/100
        </div>
        <div style="
            width:{width}px; 
            height:{height}px; 
            position:relative; 
            overflow:hidden;
        ">
            <div style="
                width:{width}px; 
                height:{height*2}px; 
                background-color:#f0f0f0; 
                border-radius:50%; 
                position:absolute; 
                top:0;
            "></div>
            <div style="
                width:{width}px; 
                height:{height*2}px; 
                background-color:{color}; 
                border-radius:50%; 
                position:absolute; 
                top:0;
                clip-path: polygon(50% 50%, 0 0, {angle}% 0);
                transform: rotate({90-angle/2}deg);
            "></div>
            <div style="
                width:{width-40}px; 
                height:{(height-20)*2}px; 
                background-color:white; 
                border-radius:50%; 
                position:absolute; 
                top:10px;
                left:20px;
            "></div>
            <div style="
                width:10px; 
                height:{height/2}px; 
                background-color:#333; 
                position:absolute; 
                top:{height/2}px;
                left:{width/2-5}px;
                transform-origin: bottom center;
                transform: rotate({angle-90}deg);
                border-radius:5px;
            "></div>
            <div style="
                width:20px; 
                height:20px; 
                background-color:#333; 
                border-radius:50%;
                position:absolute; 
                top:{height/2-10}px;
                left:{width/2-10}px;
            "></div>
        </div>
        <div style="
            display:flex; 
            justify-content:space-between; 
            margin-top:5px;
            font-size:12px;
            color:#666;
        ">
            <span>0</span>
            <span>50</span>
            <span>100</span>
        </div>
    </div>
    """
    
    return html

def generate_score_chart(scores):
    """
    Generate a simple bar chart for question scores
    
    Args:
        scores (list): List of score dictionaries with 'relevance_score' keys
        
    Returns:
        str: HTML for the score chart
    """
    if not scores:
        return "<p>No scores available</p>"
    
    score_values = [s.get("relevance_score", 0) for s in scores]
    max_score = 100
    
    # Create HTML/CSS bar chart
    html = """
    <div style="margin-top:20px;">
        <div style="display:flex; height:200px; align-items:flex-end; margin-bottom:5px;">
    """
    
    # Add bars
    for i, score in enumerate(score_values):
        # Set bar color based on score
        if score >= 80:
            color = "#28a745"  # Green
        elif score >= 60:
            color = "#ffc107"  # Yellow
        else:
            color = "#dc3545"  # Red
            
        # Calculate height percentage
        height_percent = (score / max_score) * 100
        
        # Add bar element
        html += f"""
        <div style="
            flex:1; 
            margin:0 2px; 
            height:{height_percent}%; 
            background-color:{color};
            position:relative;
            border-radius:3px 3px 0 0;
        ">
            <div style="
                position:absolute; 
                top:-25px; 
                width:100%; 
                text-align:center; 
                font-size:12px;
            ">
                {score}
            </div>
        </div>
        """
    
    # Close bar container
    html += """
        </div>
        <div style="display:flex; margin-top:5px;">
    """
    
    # Add labels
    for i in range(len(score_values)):
        html += f"""
        <div style="flex:1; text-align:center; font-size:12px;">Q{i+1}</div>
        """
    
    # Close labels container and main div
    html += """
        </div>
    </div>
    """
    
    return html

def display_score_visualization(scores):
    """
    Display visualizations of the interview scores.
    
    Args:
        scores (list): List of score dictionaries
    """
    if not scores:
        st.warning("No scores available to visualize")
        return
    
    # Calculate average score
    avg_score = sum(s.get("relevance_score", 0) for s in scores) / len(scores)
    avg_score = round(avg_score, 1)  # Round to 1 decimal place
    
    # Create two columns for the visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Average Relevance Score")
        # Use st.components.v1.html instead of st.markdown for HTML rendering
        st.components.v1.html(create_score_gauge(avg_score), height=180, scrolling=False)
    
    with col2:
        st.markdown("### Question-by-Question Scores")
        # Use st.components.v1.html for the chart too
        st.components.v1.html(generate_score_chart(scores), height=250, scrolling=False)
    
    # Add score distribution
    st.markdown("### Score Distribution")
    
    # Count scores in each category
    excellent = sum(1 for s in scores if s.get("relevance_score", 0) >= 80)
    good = sum(1 for s in scores if 60 <= s.get("relevance_score", 0) < 80)
    needs_improvement = sum(1 for s in scores if s.get("relevance_score", 0) < 60)
    
    # Alternative: Use Streamlit's native components for the distribution
    dist_data = {
        "Category": ["Excellent", "Good", "Needs Work"],
        "Count": [excellent, good, needs_improvement],
        "Color": ["#28a745", "#ffc107", "#dc3545"]
    }
    df = pd.DataFrame(dist_data)
    
    # Display as a horizontal bar chart
    st.bar_chart(df.set_index("Category")["Count"])
    
    # Or create a custom HTML version if you prefer the original styling
    distribution_html = f"""
    <div style="display:flex; margin-top:10px;">
        <div style="
            flex:{max(excellent, 1)}; 
            background-color:#28a745; 
            color:white; 
            text-align:center; 
            padding:5px 0;
            border-radius:3px 0 0 3px;
        ">
            {excellent} Excellent
        </div>
        <div style="
            flex:{max(good, 1)}; 
            background-color:#ffc107; 
            color:white; 
            text-align:center; 
            padding:5px 0;
        ">
            {good} Good
        </div>
        <div style="
            flex:{max(needs_improvement, 1)}; 
            background-color:#dc3545; 
            color:white; 
            text-align:center; 
            padding:5px 0;
            border-radius:0 3px 3px 0;
        ">
            {needs_improvement} Needs Work
        </div>
    </div>
    """
    
    # Use st.components.v1.html for the distribution visualization
    st.components.v1.html(distribution_html, height=50, scrolling=False)

# Example usage (add this to show how to call the function)
if __name__ == "__main__":
    st.title("Interview Score Visualization")
    
    # Example data for demonstration
    example_scores = [
        {"relevance_score": 85},
        {"relevance_score": 65},
        {"relevance_score": 92},
        {"relevance_score": 45},
        {"relevance_score": 78}
    ]
    
    # Toggle for showing example data
    show_example = st.checkbox("Show example visualization")
    
    if show_example:
        display_score_visualization(example_scores)
    else:
        st.info("Check the box above to see an example visualization")