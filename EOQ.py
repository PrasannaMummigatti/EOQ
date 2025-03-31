import numpy as np
from bokeh.layouts import column
from bokeh.models import CustomJS, Slider, Div,Span
from bokeh.plotting import figure, show

# Initial values
D = 1000   # Annual demand
Ct = 50    # Reordering cost per order
Ce = 9     # Holding cost per unit per year

# Compute initial EOQ
EOQ_value = np.sqrt((2 * Ct * D) / Ce)

# Order quantity range for cost plot
Q_values = np.linspace(1, 2000, 200)  # Avoid Q=0 to prevent division errors
Ordering_Cost_values = (D / Q_values) * Ct
Holding_Cost_values = (Q_values / 2) * Ce
Total_Cost_values = Ordering_Cost_values + Holding_Cost_values  # Total Cost

# Create figure
p = figure(width=700, height=450, title="Economic Order Quantity (EOQ) and Annual Cost",
           x_axis_label="Order Quantity (Q)", y_axis_label="Annual Cost",x_range=[0,200],y_range=[0,4000])

#p.sizing_mode="stretch_width"


# Plot Total Cost curve
cost_line = p.line(Q_values, Total_Cost_values, line_width=2, color="blue", legend_label="Total Cost")

# Plot Ordering Cost curve
ordering_cost_line = p.line(Q_values, Ordering_Cost_values, line_width=2, color="green", legend_label="Ordering Cost")

# Plot Holding Cost curve
holding_cost_line = p.line(Q_values, Holding_Cost_values, line_width=2, color="orange", legend_label="Holding Cost")

# Plot EOQ as a red dot
EOQ_cost = (D / EOQ_value) * Ct + (EOQ_value / 2) * Ce
EOQ_point = p.scatter(x=[EOQ_value], y=[EOQ_cost], size=12, color="red", legend_label="EOQ")

# Add Vertical Line at EOQ (Order Quantity)
vline = Span(location=EOQ_value, dimension='height', line_color='red', line_width=2, line_dash='dashed')

# Add Horizontal Line at EOQ Cost (Total Cost)
hline = Span(location=EOQ_cost, dimension='width', line_color='red', line_width=2, line_dash='dashed')

p.add_layout(vline)  # Add vertical line to plot
p.add_layout(hline)  # Add horizontal line to plot

# Output text
output_text = Div(text=f"<h3>EOQ: {EOQ_value:.2f}       Total Cost: {EOQ_cost:.2f} units</h3>", width=400, height=50)

# Sliders for inputs
D_slider = Slider(start=100, end=4000, value=D, step=50, title="Annual Demand (D)")
Ct_slider = Slider(start=10, end=200, value=Ct, step=5, title="Reordering Cost per Order (Ct)")
Ce_slider = Slider(start=1, end=50, value=Ce, step=0.5, title="Holding Cost per Unit per Year (Ce)")

# CustomJS callback to update EOQ and cost curves
callback = CustomJS(args=dict(cost_line=cost_line, ordering_cost_line=ordering_cost_line, 
                              holding_cost_line=holding_cost_line, EOQ_point=EOQ_point, 
                              output_text=output_text, vline=vline, hline=hline,
                              D_slider=D_slider, Ct_slider=Ct_slider, Ce_slider=Ce_slider), code="""
    const D = D_slider.value;
    const Ct = Ct_slider.value;
    const Ce = Ce_slider.value;
    
    // Compute EOQ
    const EOQ = Math.sqrt((2 * Ct * D) / Ce);
    
    // Get existing Q values
    const Q_values = cost_line.data_source.data.x;
    
    // Compute costs
    const Ordering_Cost_values = Q_values.map(Q => (D / Q) * Ct);
    const Holding_Cost_values = Q_values.map(Q => (Q / 2) * Ce);
    const Total_Cost_values = Ordering_Cost_values.map((oc, i) => oc + Holding_Cost_values[i]);

    // Update curves
    cost_line.data_source.data.y = Total_Cost_values;
    ordering_cost_line.data_source.data.y = Ordering_Cost_values;
    holding_cost_line.data_source.data.y = Holding_Cost_values;
    
    cost_line.data_source.change.emit();
    ordering_cost_line.data_source.change.emit();
    holding_cost_line.data_source.change.emit();
    
    // Update EOQ point
    const EOQ_cost = (D / EOQ) * Ct + (EOQ / 2) * Ce;
    EOQ_point.data_source.data.x = [EOQ];
    EOQ_point.data_source.data.y = [EOQ_cost];
    EOQ_point.data_source.change.emit();

    // Update vertical and horizontal lines
    vline.location = EOQ;  // Move vertical line to new EOQ
    hline.location = EOQ_cost;  // Move horizontal line to new total cost

    // Update displayed text
    output_text.text = `<h3>EOQ: ${EOQ.toFixed(2)} units  Total Cost: ${EOQ_cost.toFixed(2)}</h3>`;

""")

# Link sliders to callback
D_slider.js_on_change('value', callback)
Ct_slider.js_on_change('value', callback)
Ce_slider.js_on_change('value', callback)

# Layout and show
layout = column(p, output_text, D_slider, Ct_slider, Ce_slider)
show(layout)
