import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="5G Frame Structure Visualizer", layout="wide", page_icon="📋")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📋 5G NR Frame Structure Visualizer</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("5G NR Structure")
app_mode = st.sidebar.selectbox(
    "Choose Module",
    [
        "🕐 Frame & Slot Structure",
        "📊 Resource Grid",
        "📡 Physical Channels",
        "🎯 Reference Signals",
        "⏱️ Time Domain Analysis",
        "🔧 TDD Configuration"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Visualize 5G NR frame structure, resource grids, physical channels, "
    "and reference signals. Understand how 5G organizes time and frequency resources."
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_slot_params(scs_khz):
    """Get slot parameters based on subcarrier spacing"""
    mu_map = {15: 0, 30: 1, 60: 2, 120: 3, 240: 4}
    mu = mu_map[scs_khz]
    
    slot_duration_ms = 1.0 / (2**mu)
    slots_per_subframe = 2**mu
    slots_per_frame = 10 * slots_per_subframe
    
    return {
        'mu': mu,
        'slot_duration_ms': slot_duration_ms,
        'slots_per_subframe': slots_per_subframe,
        'slots_per_frame': slots_per_frame,
        'symbols_per_slot': 14  # Normal CP
    }

def create_dmrs_pattern(num_rbs, num_symbols, dmrs_type='Type1', dmrs_positions=[2, 11]):
    """Create DMRS pattern for resource grid"""
    grid = np.zeros((num_symbols, num_rbs * 12), dtype=int)
    
    if dmrs_type == 'Type1':
        # DMRS Type 1: Every other subcarrier
        for sym_idx in dmrs_positions:
            if sym_idx < num_symbols:
                grid[sym_idx, ::2] = 1  # Every other subcarrier
    elif dmrs_type == 'Type2':
        # DMRS Type 2: Two consecutive subcarriers out of 6
        for sym_idx in dmrs_positions:
            if sym_idx < num_symbols:
                for sc_idx in range(0, num_rbs * 12, 6):
                    if sc_idx < num_rbs * 12 - 1:
                        grid[sym_idx, sc_idx:sc_idx+2] = 1
    
    return grid

def create_pdcch_region(num_rbs, num_symbols, coreset_duration=2):
    """Create PDCCH control region"""
    grid = np.zeros((num_symbols, num_rbs * 12), dtype=int)
    
    # CORESET (Control Resource Set) - first few symbols
    for sym_idx in range(min(coreset_duration, num_symbols)):
        grid[sym_idx, :] = 1
    
    return grid

# ============================================================================
# 1. FRAME & SLOT STRUCTURE
# ============================================================================
if app_mode == "🕐 Frame & Slot Structure":
    st.markdown('<p class="section-header">🕐 5G NR Frame & Slot Structure</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Numerology Selection")
        
        scs_options = {
            '15 kHz (μ=0)': 15,
            '30 kHz (μ=1)': 30,
            '60 kHz (μ=2)': 60,
            '120 kHz (μ=3)': 120,
            '240 kHz (μ=4)': 240
        }
        
        scs_label = st.selectbox("Subcarrier Spacing", list(scs_options.keys()), index=1)
        scs_khz = scs_options[scs_label]
        
        params = get_slot_params(scs_khz)
        
        st.markdown("### Display Options")
        view_level = st.radio(
            "View Level",
            ["Frame (10 ms)", "Subframe (1 ms)", "Slot", "Symbol"],
            index=2
        )
        
        if view_level == "Slot":
            slot_idx = st.slider("Slot Index", 0, params['slots_per_frame']-1, 0)
        
        show_timing = st.checkbox("Show Timing Information", value=True)
    
    with col2:
        if view_level == "Frame (10 ms)":
            st.markdown("### Radio Frame Structure (10 ms)")
            
            # Create frame visualization
            fig = go.Figure()
            
            # Draw 10 subframes
            for sf in range(10):
                fig.add_shape(
                    type="rect",
                    x0=sf, x1=sf+1, y0=0, y1=1,
                    line=dict(color="blue", width=2),
                    fillcolor="lightblue", opacity=0.3
                )
                fig.add_annotation(
                    x=sf+0.5, y=0.5,
                    text=f"SF {sf}",
                    showarrow=False,
                    font=dict(size=14)
                )
            
            fig.update_layout(
                title=f"Radio Frame (10 subframes, {params['slots_per_frame']} slots @ {scs_khz} kHz SCS)",
                xaxis=dict(title="Time (ms)", range=[0, 10], showgrid=True),
                yaxis=dict(showticklabels=False, range=[0, 1]),
                height=200,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Slot breakdown
            st.markdown("### Slot Distribution per Subframe")
            
            fig2 = go.Figure()
            
            slot_width = 1.0 / params['slots_per_subframe']
            
            for sf in range(10):
                for slot in range(params['slots_per_subframe']):
                    x_start = sf + slot * slot_width
                    x_end = x_start + slot_width
                    
                    fig2.add_shape(
                        type="rect",
                        x0=x_start, x1=x_end, y0=0, y1=1,
                        line=dict(color="green", width=1),
                        fillcolor="lightgreen", opacity=0.5
                    )
            
            fig2.update_layout(
                title=f"All {params['slots_per_frame']} Slots in Frame ({params['slots_per_subframe']} slots/subframe)",
                xaxis=dict(title="Time (ms)", range=[0, 10]),
                yaxis=dict(showticklabels=False, range=[0, 1]),
                height=200,
                showlegend=False
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        elif view_level == "Subframe (1 ms)":
            st.markdown("### Subframe Structure (1 ms)")
            
            fig = go.Figure()
            
            slot_width_ms = params['slot_duration_ms']
            
            for slot in range(params['slots_per_subframe']):
                x_start = slot * slot_width_ms
                x_end = x_start + slot_width_ms
                
                fig.add_shape(
                    type="rect",
                    x0=x_start, x1=x_end, y0=0, y1=1,
                    line=dict(color="blue", width=2),
                    fillcolor="lightblue", opacity=0.5
                )
                fig.add_annotation(
                    x=(x_start + x_end)/2, y=0.5,
                    text=f"Slot {slot}",
                    showarrow=False,
                    font=dict(size=12)
                )
            
            fig.update_layout(
                title=f"Subframe = {params['slots_per_subframe']} Slots ({slot_width_ms:.3f} ms each)",
                xaxis=dict(title="Time (ms)", range=[0, 1]),
                yaxis=dict(showticklabels=False, range=[0, 1]),
                height=250,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif view_level == "Slot":
            st.markdown(f"### Slot {slot_idx} Structure")
            
            fig = go.Figure()
            
            symbol_duration_ms = params['slot_duration_ms'] / params['symbols_per_slot']
            
            for sym in range(params['symbols_per_slot']):
                x_start = sym * symbol_duration_ms
                x_end = x_start + symbol_duration_ms
                
                color = "lightblue" if sym % 2 == 0 else "lightcoral"
                
                fig.add_shape(
                    type="rect",
                    x0=x_start, x1=x_end, y0=0, y1=1,
                    line=dict(color="black", width=1),
                    fillcolor=color, opacity=0.6
                )
                fig.add_annotation(
                    x=(x_start + x_end)/2, y=0.5,
                    text=str(sym),
                    showarrow=False,
                    font=dict(size=10)
                )
            
            fig.update_layout(
                title=f"Slot = {params['symbols_per_slot']} OFDM Symbols ({symbol_duration_ms*1000:.2f} μs each)",
                xaxis=dict(title="Time (ms)", range=[0, params['slot_duration_ms']]),
                yaxis=dict(showticklabels=False, range=[0, 1]),
                height=250,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:  # Symbol level
            st.markdown("### OFDM Symbol Structure")
            
            symbol_duration_ms = params['slot_duration_ms'] / params['symbols_per_slot']
            symbol_duration_us = symbol_duration_ms * 1000
            
            # CP duration (approximate)
            if scs_khz <= 30:
                cp_ratio_first = 0.071  # First symbol
                cp_ratio_others = 0.0694
            else:
                cp_ratio_first = 0.06
                cp_ratio_others = 0.059
            
            cp_duration_first = symbol_duration_us * cp_ratio_first
            cp_duration_others = symbol_duration_us * cp_ratio_others
            useful_duration = symbol_duration_us * (1 - cp_ratio_others)
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('First Symbol (longer CP)', 'Other Symbols'),
                vertical_spacing=0.15
            )
            
            # First symbol
            fig.add_shape(
                type="rect",
                x0=0, x1=cp_duration_first, y0=0, y1=1,
                fillcolor="green", opacity=0.5,
                line=dict(color="black"),
                row=1, col=1
            )
            fig.add_annotation(
                x=cp_duration_first/2, y=0.5,
                text="CP",
                showarrow=False,
                row=1, col=1
            )
            
            fig.add_shape(
                type="rect",
                x0=cp_duration_first, x1=symbol_duration_us, y0=0, y1=1,
                fillcolor="blue", opacity=0.5,
                line=dict(color="black"),
                row=1, col=1
            )
            fig.add_annotation(
                x=(cp_duration_first + symbol_duration_us)/2, y=0.5,
                text="Useful Symbol (FFT)",
                showarrow=False,
                row=1, col=1
            )
            
            # Other symbols
            fig.add_shape(
                type="rect",
                x0=0, x1=cp_duration_others, y0=0, y1=1,
                fillcolor="green", opacity=0.5,
                line=dict(color="black"),
                row=2, col=1
            )
            fig.add_annotation(
                x=cp_duration_others/2, y=0.5,
                text="CP",
                showarrow=False,
                row=2, col=1
            )
            
            fig.add_shape(
                type="rect",
                x0=cp_duration_others, x1=symbol_duration_us, y0=0, y1=1,
                fillcolor="blue", opacity=0.5,
                line=dict(color="black"),
                row=2, col=1
            )
            fig.add_annotation(
                x=(cp_duration_others + symbol_duration_us)/2, y=0.5,
                text="Useful Symbol (FFT)",
                showarrow=False,
                row=2, col=1
            )
            
            fig.update_xaxes(title_text="Time (μs)", row=1, col=1)
            fig.update_xaxes(title_text="Time (μs)", row=2, col=1)
            fig.update_yaxes(showticklabels=False, row=1, col=1)
            fig.update_yaxes(showticklabels=False, row=2, col=1)
            
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    if show_timing:
        st.markdown("### Timing Parameters Summary")
        
        col_a, col_b, col_c, col_d, col_e = st.columns(5)
        
        with col_a:
            st.metric("Numerology (μ)", params['mu'])
        with col_b:
            st.metric("SCS (kHz)", scs_khz)
        with col_c:
            st.metric("Slot Duration", f"{params['slot_duration_ms']:.3f} ms")
        with col_d:
            st.metric("Slots/Frame", params['slots_per_frame'])
        with col_e:
            st.metric("Symbols/Slot", params['symbols_per_slot'])
        
        # Detailed timing table
        symbol_duration_us = params['slot_duration_ms'] * 1000 / params['symbols_per_slot']
        
        timing_df = pd.DataFrame({
            'Parameter': [
                'Radio Frame',
                'Subframe',
                'Slot',
                'OFDM Symbol',
                'Slots per Frame',
                'Slots per Subframe',
                'Symbols per Slot'
            ],
            'Duration': [
                '10 ms',
                '1 ms',
                f'{params["slot_duration_ms"]:.4f} ms',
                f'{symbol_duration_us:.3f} μs',
                '-',
                '-',
                '-'
            ],
            'Count': [
                '1',
                '10',
                f'{params["slots_per_frame"]}',
                f'{params["symbols_per_slot"] * params["slots_per_frame"]}',
                f'{params["slots_per_frame"]}',
                f'{params["slots_per_subframe"]}',
                f'{params["symbols_per_slot"]}'
            ]
        })
        
        st.dataframe(timing_df, use_container_width=True)
    
    with st.expander("📚 Theory: 5G NR Frame Structure"):
        st.markdown("""
        ### Frame Hierarchy
        
        **5G NR time domain hierarchy:**
        
        ```
        Radio Frame (10 ms)
        └── Subframe (1 ms) × 10
            └── Slot (variable) × 2^μ
                └── OFDM Symbol (variable) × 14 (normal CP)
        ```
        
        ### Radio Frame
        
        - **Duration:** Always 10 ms (fixed)
        - **Contains:** 10 subframes
        - **Frame number:** System Frame Number (SFN), 0-1023 (repeats every 10.24 seconds)
        
        ### Subframe
        
        - **Duration:** Always 1 ms (fixed)
        - **Contains:** $2^\\mu$ slots
        - Used for TDD UL/DL configuration
        
        ### Slot
        
        - **Duration:** $T_{slot} = \\frac{1}{2^\\mu}$ ms
        - **Contains:** 14 OFDM symbols (normal CP) or 12 (extended CP)
        - Basic scheduling unit in 5G NR
        
        | μ | SCS | Slot Duration | Slots/Subframe | Slots/Frame |
        |---|-----|---------------|----------------|-------------|
        | 0 | 15 kHz | 1.0 ms | 1 | 10 |
        | 1 | 30 kHz | 0.5 ms | 2 | 20 |
        | 2 | 60 kHz | 0.25 ms | 4 | 40 |
        | 3 | 120 kHz | 0.125 ms | 8 | 80 |
        | 4 | 240 kHz | 0.0625 ms | 16 | 160 |
        
        ### OFDM Symbol
        
        - **Duration:** $T_{symbol} = \\frac{T_{slot}}{14}$
        - **Consists of:** Cyclic Prefix + Useful Symbol
        - **CP duration:** Longer for first symbol, shorter for others
        
        **Why different CP lengths?**
        - Allows FFT window to be exactly $1/\\Delta f$
        - Total slot duration remains constant
        
        ### Cyclic Prefix
        
        **Normal CP (most common):**
        - First symbol: ≈ 5.2 μs at 15 kHz SCS
        - Other symbols: ≈ 4.7 μs at 15 kHz SCS
        - Scales with numerology (divide by $2^\mu$)
        
        **Extended CP (only for μ=2, 60 kHz):**
        - Longer CP with 12 symbols per slot
        - Used for high delay spread scenarios
        
        ### Mini-Slots
        
        For **ultra-low latency** applications:
        - Can be 2, 4, or 7 symbols
        - Allows faster scheduling
        - Used for URLLC (Ultra-Reliable Low Latency Communication)
        
        ### Time Domain Flexibility
        
        Unlike LTE (fixed 1 ms TTI), 5G NR offers:
        - **Slot-based scheduling:** 14 symbols
        - **Non-slot scheduling:** Flexible start/duration
        - **Mini-slots:** 2-13 symbols
        - Enables diverse latency requirements
        """)

# ============================================================================
# 2. RESOURCE GRID
# ============================================================================
elif app_mode == "📊 Resource Grid":
    st.markdown('<p class="section-header">📊 5G NR Resource Grid</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Grid Configuration")
        
        num_rbs = st.slider("Number of RBs", 10, 100, 52, 1)
        num_symbols = st.slider("Number of Symbols", 7, 14, 14, 1)
        
        scs_grid = st.selectbox("Subcarrier Spacing", [15, 30, 60, 120], index=1)
        
        st.markdown("### Channel Allocation")
        
        show_dmrs = st.checkbox("Show DMRS", value=True)
        show_pdcch = st.checkbox("Show PDCCH Region", value=True)
        show_pdsch = st.checkbox("Show PDSCH Region", value=True)
        
        if show_dmrs:
            dmrs_type = st.radio("DMRS Type", ["Type1", "Type2"])
            dmrs_symbols = st.multiselect(
                "DMRS Symbol Positions",
                list(range(num_symbols)),
                default=[2, 11] if num_symbols >= 12 else [2]
            )
        
        if show_pdcch:
            coreset_duration = st.slider("CORESET Duration (symbols)", 1, 3, 2)
    
    # Create resource grid
    total_subcarriers = num_rbs * 12
    grid_allocation = np.zeros((num_symbols, total_subcarriers))
    
    # PDSCH (data) - fill everything first
    if show_pdsch:
        grid_allocation[:, :] = 1  # PDSCH
    
    # PDCCH (control)
    if show_pdcch:
        pdcch = create_pdcch_region(num_rbs, num_symbols, coreset_duration)
        grid_allocation[pdcch == 1] = 2  # Override with PDCCH
    
    # DMRS
    if show_dmrs:
        dmrs = create_dmrs_pattern(num_rbs, num_symbols, dmrs_type, dmrs_symbols)
        grid_allocation[dmrs == 1] = 3  # Override with DMRS
    
    with col2:
        st.markdown("### Resource Grid Visualization")
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=grid_allocation,
            colorscale=[
                [0, 'white'],      # Empty
                [0.33, 'lightblue'],  # PDSCH
                [0.66, 'orange'],     # PDCCH
                [1, 'red']            # DMRS
            ],
            showscale=False,
            hovertemplate='Symbol: %{y}<br>Subcarrier: %{x}<br><extra></extra>'
        ))
        
        # Add RB boundaries
        for rb in range(1, num_rbs):
            fig.add_vline(x=rb*12-0.5, line_dash="dash", line_color="gray", opacity=0.3)
        
        fig.update_layout(
            title=f"Resource Grid: {num_rbs} RBs × {num_symbols} Symbols = {num_rbs * 12 * num_symbols} REs",
            xaxis_title="Subcarrier Index",
            yaxis_title="OFDM Symbol Index",
            height=600,
            yaxis=dict(autorange='reversed')  # Symbol 0 at top
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Legend
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.markdown("⬜ **Empty/Guard**")
        with col_b:
            st.markdown("🔵 **PDSCH (Data)**")
        with col_c:
            st.markdown("🟠 **PDCCH (Control)**")
        with col_d:
            st.markdown("🔴 **DMRS (Reference)**")
    
    # Resource statistics
    st.markdown("### Resource Element Statistics")
    
    total_res = num_rbs * 12 * num_symbols
    dmrs_res = np.sum(grid_allocation == 3)
    pdcch_res = np.sum(grid_allocation == 2)
    pdsch_res = np.sum(grid_allocation == 1)
    empty_res = np.sum(grid_allocation == 0)
    
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    
    with col_a:
        st.metric("Total REs", total_res)
    with col_b:
        st.metric("PDSCH REs", f"{pdsch_res} ({100*pdsch_res/total_res:.1f}%)")
    with col_c:
        st.metric("PDCCH REs", f"{pdcch_res} ({100*pdcch_res/total_res:.1f}%)")
    with col_d:
        st.metric("DMRS REs", f"{dmrs_res} ({100*dmrs_res/total_res:.1f}%)")
    with col_e:
        st.metric("Empty REs", f"{empty_res} ({100*empty_res/total_res:.1f}%)")
    
    # Throughput calculation
    st.markdown("### Estimated Throughput")
    
    modulation = st.selectbox("Modulation", ["QPSK", "16-QAM", "64-QAM", "256-QAM"], index=2, key='rg_mod')
    code_rate = st.slider("Code Rate", 0.1, 1.0, 0.75, 0.05, key='rg_cr')
    mimo_layers = st.selectbox("MIMO Layers", [1, 2, 4, 8], index=1, key='rg_mimo')
    
    bits_per_symbol = {"QPSK": 2, "16-QAM": 4, "64-QAM": 6, "256-QAM": 8}[modulation]
    
    params_grid = get_slot_params(scs_grid)
    slots_per_second = 1000 / params_grid['slot_duration_ms']
    
    bits_per_slot = pdsch_res * bits_per_symbol * code_rate * mimo_layers
    throughput_mbps = bits_per_slot * slots_per_second / 1e6
    
    st.info(f"""
    **Throughput:** {throughput_mbps:.2f} Mbps
    
    Calculation:
    - PDSCH REs per slot: {pdsch_res}
    - Bits per RE: {bits_per_symbol} × {code_rate} = {bits_per_symbol * code_rate:.2f}
    - MIMO layers: {mimo_layers}
    - Slots/sec: {slots_per_second:.0f}
    """)
    
    with st.expander("📚 Theory: Resource Grid"):
        st.markdown("""
        ### Resource Grid Basics
        
        **Resource Element (RE):**
        - Smallest resource unit
        - 1 subcarrier × 1 OFDM symbol
        - Carries one modulation symbol
        
        **Resource Block (RB):**
        - 12 consecutive subcarriers
        - 1 slot in time (14 or 12 symbols)
        - Basic scheduling unit
        - Size in frequency: 12 × SCS (e.g., 180 kHz @ 15 kHz SCS)
        
        ### Grid Structure
        
        **Frequency domain:**
        - Organized in Resource Blocks (RBs)
        - Each RB = 12 subcarriers
        - Total bandwidth = N_RB × 12 × SCS
        
        **Time domain:**
        - Organized in slots
        - Each slot = 14 OFDM symbols (normal CP)
        - Flexible scheduling: can allocate any number of symbols
        
        ### Channel Mapping
        
        **PDCCH (Physical Downlink Control Channel):**
        - Carries DCI (Downlink Control Information)
        - Scheduling grants, power control, etc.
        - Located in CORESET (Control Resource Set)
        - Typically first 1-3 symbols
        - Uses lower modulation (QPSK typically) for robustness
        
        **PDSCH (Physical Downlink Shared Channel):**
        - Carries user data (DL-SCH transport channel)
        - Scheduled by PDCCH
        - Uses remaining REs after control and reference signals
        - Adaptive modulation: QPSK to 256-QAM
        
        **DMRS (Demodulation Reference Signal):**
        - Used for channel estimation
        - Allows coherent demodulation
        - Two types:
          - **Type 1:** Every other subcarrier (50% density)
                    - **Type 2:** 2 out of 6 subcarriers (lower density, supports more CDM ports)
        - Typically in symbols 2 and 11 (front-loaded)
        - Can add additional DMRS for high Doppler
        
        ### Resource Allocation
        
        **Time domain:**
        - Slot-based: Entire slot
        - Non-slot: Start symbol + duration
        - Mini-slot: 2, 4, or 7 symbols
        
        **Frequency domain:**
        - Type 0: Bitmap of RB groups
        - Type 1: Start RB + number of RBs
        
        ### Overhead Analysis
        
        **Typical overhead sources:**
        1. **DMRS:** 5-15% (depends on configuration)
        2. **PDCCH:** 5-10% (depends on CORESET size)
        3. **CSI-RS:** 1-3% (periodic reference signals)
        4. **Guard bands:** ~5%
        5. **Synchronization:** SSB overhead
        
        **Total overhead:** Typically 15-30%
        - More overhead → better channel estimation, control
        - Less overhead → higher throughput
        - Trade-off based on channel conditions
        
        ### Slot Format
        
        5G NR supports flexible slot formats:
        - **D:** Downlink symbols
        - **U:** Uplink symbols
        - **X:** Flexible (can be D or U)
        
        Example: DDDDDXXXUU
        - 5 DL symbols
        - 3 flexible symbols
        - 2 UL symbols
        
        Configured via TDD configuration in SIB1.
        """)

# ============================================================================
# 3. PHYSICAL CHANNELS
# ============================================================================
elif app_mode == "📡 Physical Channels":
    st.markdown('<p class="section-header">📡 5G NR Physical Channels</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📥 Downlink Channels", "📤 Uplink Channels"])
    
    with tab1:
        st.markdown("### Downlink Physical Channels")
        
        dl_channels = {
            'PDSCH': {
                'name': 'Physical Downlink Shared Channel',
                'purpose': 'Carries user data and higher layer signaling',
                'transport': 'DL-SCH (Downlink Shared Channel)',
                'modulation': 'QPSK, 16-QAM, 64-QAM, 256-QAM',
                'coding': 'LDPC',
                'scheduling': 'Dynamic (per slot)',
                'typical_symbols': '12-13 symbols/slot',
                'color': 'blue'
            },
            'PDCCH': {
                'name': 'Physical Downlink Control Channel',
                'purpose': 'Carries downlink control information (DCI)',
                'transport': 'DCI formats (0, 1, 2, etc.)',
                'modulation': 'QPSK',
                'coding': 'Polar',
                'scheduling': 'CORESET configuration',
                'typical_symbols': '1-3 symbols/slot',
                'color': 'orange'
            },
            'PBCH': {
                'name': 'Physical Broadcast Channel',
                'purpose': 'Carries essential system information (MIB)',
                'transport': 'BCH (Broadcast Channel)',
                'modulation': 'QPSK',
                'coding': 'Polar',
                'scheduling': 'Fixed (SSB)',
                'typical_symbols': 'Part of SSB (4 symbols)',
                'color': 'green'
            }
        }
        
        # Channel selector
        selected_dl = st.selectbox("Select Channel", list(dl_channels.keys()))
        
        ch_info = dl_channels[selected_dl]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {ch_info['name']}")
            st.markdown(f"""
            **Purpose:** {ch_info['purpose']}
            
            **Transport Channel:** {ch_info['transport']}
            
            **Modulation:** {ch_info['modulation']}
            
            **Channel Coding:** {ch_info['coding']}
            
            **Scheduling:** {ch_info['scheduling']}
            
            **Typical Allocation:** {ch_info['typical_symbols']}
            """)
        
        with col2:
            # Visual representation
            fig = go.Figure()
            
            if selected_dl == 'PDSCH':
                # PDSCH occupies most symbols except PDCCH
                symbols = list(range(14))
                allocation = [0.3] * 2 + [1.0] * 12  # First 2 for PDCCH
                colors = ['orange'] * 2 + ['blue'] * 12
                
            elif selected_dl == 'PDCCH':
                symbols = list(range(14))
                allocation = [1.0] * 2 + [0] * 12  # First 2 symbols
                colors = ['orange'] * 2 + ['lightgray'] * 12
                
            else:  # PBCH
                symbols = list(range(14))
                allocation = [1.0] * 4 + [0] * 10  # SSB occupies 4 symbols
                colors = ['green'] * 4 + ['lightgray'] * 10
            
            fig.add_trace(go.Bar(
                x=symbols,
                y=allocation,
                marker=dict(color=colors),
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"{selected_dl} Typical Slot Allocation",
                xaxis_title="OFDM Symbol",
                yaxis_title="Allocation",
                height=400,
                yaxis=dict(range=[0, 1.2])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # DCI formats for PDCCH
        if selected_dl == 'PDCCH':
            st.markdown("### DCI Formats")
            
            dci_formats = pd.DataFrame({
                'Format': ['0_0', '0_1', '1_0', '1_1', '2_0', '2_1'],
                'Purpose': [
                    'UL scheduling (fallback)',
                    'UL scheduling (normal)',
                    'DL scheduling (fallback)',
                    'DL scheduling (normal)',
                    'Slot format indication',
                    'Preemption indication'
                ],
                'Size': ['Compact', 'Large', 'Compact', 'Large', 'Small', 'Small'],
                'Use Case': [
                    'Initial access, power saving',
                    'Normal operation',
                    'Initial access, power saving',
                    'Normal operation',
                    'TDD configuration',
                    'URLLC preemption'
                ]
            })
            
            st.dataframe(dci_formats, use_container_width=True)
    
    with tab2:
        st.markdown("### Uplink Physical Channels")
        
        ul_channels = {
            'PUSCH': {
                'name': 'Physical Uplink Shared Channel',
                'purpose': 'Carries user data and higher layer signaling',
                'transport': 'UL-SCH (Uplink Shared Channel)',
                'modulation': 'π/2-BPSK, QPSK, 16-QAM, 64-QAM, 256-QAM',
                'coding': 'LDPC',
                'scheduling': 'Dynamic (granted by PDCCH)',
                'typical_symbols': '4-14 symbols',
                'color': 'purple'
            },
            'PUCCH': {
                'name': 'Physical Uplink Control Channel',
                'purpose': 'Carries uplink control information (UCI)',
                'transport': 'UCI (HARQ-ACK, CSI, SR)',
                'modulation': 'QPSK, π/2-BPSK',
                'coding': 'Sequence-based (formats 0/1), Polar (formats 2/3/4)',
                'scheduling': 'Semi-static configuration',
                'typical_symbols': '1-14 symbols',
                'color': 'teal'
            },
            'PRACH': {
                'name': 'Physical Random Access Channel',
                'purpose': 'Random access preamble transmission',
                'transport': 'Random Access Preamble',
                'modulation': 'Zadoff-Chu sequences',
                'coding': 'None (sequence-based)',
                'scheduling': 'Configured RACH occasions',
                'typical_symbols': '1-14 symbols (format dependent)',
                'color': 'brown'
            }
        }
        
        selected_ul = st.selectbox("Select Channel", list(ul_channels.keys()), key='ul_ch')
        
        ch_info_ul = ul_channels[selected_ul]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {ch_info_ul['name']}")
            st.markdown(f"""
            **Purpose:** {ch_info_ul['purpose']}
            
            **Transport Channel:** {ch_info_ul['transport']}
            
            **Modulation:** {ch_info_ul['modulation']}
            
            **Channel Coding:** {ch_info_ul['coding']}
            
            **Scheduling:** {ch_info_ul['scheduling']}
            
            **Typical Allocation:** {ch_info_ul['typical_symbols']}
            """)
        
        with col2:
            fig = go.Figure()
            
            symbols = list(range(14))
            
            if selected_ul == 'PUSCH':
                allocation = [0] * 4 + [1.0] * 10  # Skip first few symbols for PUCCH
                colors = ['lightgray'] * 4 + ['purple'] * 10
                
            elif selected_ul == 'PUCCH':
                allocation = [1.0] * 2 + [0] * 12  # First 2 symbols
                colors = ['teal'] * 2 + ['lightgray'] * 12
                
            else:  # PRACH
                allocation = [0] * 6 + [1.0] * 6 + [0] * 2
                colors = ['lightgray'] * 6 + ['brown'] * 6 + ['lightgray'] * 2
            
            fig.add_trace(go.Bar(
                x=symbols,
                y=allocation,
                marker=dict(color=colors),
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"{selected_ul} Typical Slot Allocation",
                xaxis_title="OFDM Symbol",
                yaxis_title="Allocation",
                height=400,
                yaxis=dict(range=[0, 1.2])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # UCI for PUCCH
        if selected_ul == 'PUCCH':
            st.markdown("### UCI (Uplink Control Information)")
            
            uci_info = pd.DataFrame({
                'Type': ['HARQ-ACK', 'CSI', 'SR'],
                'Purpose': [
                    'ACK/NACK for received data',
                    'Channel State Information (CQI, PMI, RI)',
                    'Scheduling Request'
                ],
                'Size': ['1-2 bits per TB', '4-100+ bits', '1 bit'],
                'Priority': ['High', 'Medium', 'Medium']
            })
            
            st.dataframe(uci_info, use_container_width=True)
    
    with st.expander("📚 Theory: Physical Channels"):
        st.markdown("""
        ### Channel Hierarchy
        
        **Logical Channels** ↔ **Transport Channels** ↔ **Physical Channels**
        
        **Example (Downlink):**
        - DTCH (Logical) → DL-SCH (Transport) → PDSCH (Physical)
        
        ### Downlink Channels
        
        **PDSCH (Physical Downlink Shared Channel):**
        - Main data channel
        - Scheduled dynamically per slot
        - Uses LDPC coding (better performance than Turbo codes in LTE)
        - Supports adaptive modulation: QPSK → 256-QAM
        - Can occupy any symbols not used by control/reference
        
        **PDCCH (Physical Downlink Control Channel):**
        - Carries DCI (Downlink Control Information)
        - Located in CORESET (Control Resource Set)
        - Uses Polar coding (optimal for short messages)
        - Always QPSK for robustness
        - DCI formats: 0_x for UL, 1_x for DL, 2_x for other
        
        **PBCH (Physical Broadcast Channel):**
        - Part of SSB (SS/PBCH Block)
        - Carries MIB (Master Information Block)
        - Transmitted periodically (typically every 20 ms)
        - Essential for initial access
        
        ### Uplink Channels
        
        **PUSCH (Physical Uplink Shared Channel):**
        - Main UL data channel
        - Can use DFT-s-OFDM (for lower PAPR) or CP-OFDM
        - π/2-BPSK at low SNR (better PAPR than QPSK)
        - Supports transform precoding (DFT spread)
        
        **PUCCH (Physical Uplink Control Channel):**
        - Carries UCI (Uplink Control Information)
        - 5 formats (0-4) with different capacities/durations
        - Format 0/2: Short (1-2 symbols)
        - Format 1/3/4: Long (4-14 symbols)
        - Uses sequence-based or coded transmission
        
        **PRACH (Physical Random Access Channel):**
        - Initial access and beam recovery
        - Uses Zadoff-Chu sequences (good autocorrelation)
        - Multiple preamble formats (A0-A3, B1-B4, C0-C2)
        - Short formats (1-2 symbols) for mmWave
        - Long formats (up to 14 symbols) for sub-6 GHz
        
        ### Channel Coding
        
        **LDPC (Low-Density Parity-Check):**
        - Used for data channels (PDSCH, PUSCH)
        - Two base graphs: BG1 (large blocks), BG2 (small blocks)
        - Better performance than Turbo codes
        - Lower latency decoding
        
        **Polar:**
        - Used for control channels (PDCCH, PUCCH)
        - Achieves Shannon capacity for infinite length
        - Good performance for short messages
        - Lower complexity than Turbo codes
        
        **Sequence-based (PUCCH formats 0/1):**
        - Very short UCI on PUCCH
        - Uses predefined sequences and cyclic shifts
        """)

# ============================================================================
# 4. REFERENCE SIGNALS
# ============================================================================
elif app_mode == "🎯 Reference Signals":
    st.markdown('<p class="section-header">🎯 Reference Signals in 5G NR</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Reference signals are known sequences used for **synchronization**, **channel estimation**, 
    and **measurements**. 5G NR has several types optimized for different purposes.
    """)
    
    tab1, tab2, tab3 = st.tabs(["📊 DMRS", "🔍 CSI-RS", "📡 SSB"])
    
    with tab1:
        st.markdown("### DMRS (Demodulation Reference Signal)")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### Configuration")
            
            dmrs_config_type = st.radio("DMRS Configuration Type", ["Type 1", "Type 2"])
            dmrs_additional = st.checkbox("Additional DMRS symbols", value=False)
            
            num_cdm_groups = st.slider("Number of CDM Groups", 1, 3, 2)
            
            st.markdown("""
            **DMRS Type 1:**
            - Every other subcarrier
            - 6 REs per RB per symbol
            - Suitable for normal scenarios
            
            **DMRS Type 2:**
            - 2 consecutive out of 6 subcarriers
            - 4 REs per RB per symbol
            - Lower overhead, supports more CDM groups
            """)
        
        with col2:
            # Visualize DMRS pattern
            num_rbs_dmrs = 10
            num_symbols_dmrs = 14
            
            dmrs_grid = np.zeros((num_symbols_dmrs, num_rbs_dmrs * 12))
            
            # Front-loaded DMRS (symbols 2-3)
            dmrs_symbols_fl = [2, 3] if dmrs_additional else [2]
            
            if dmrs_config_type == "Type 1":
                for sym in dmrs_symbols_fl:
                    dmrs_grid[sym, ::2] = 1  # Every other subcarrier
            else:  # Type 2
                for sym in dmrs_symbols_fl:
                    for sc in range(0, num_rbs_dmrs * 12, 6):
                        if sc < num_rbs_dmrs * 12 - 1:
                            dmrs_grid[sym, sc:sc+2] = 1
            
            # Additional DMRS at end if high Doppler
            if dmrs_additional:
                if dmrs_config_type == "Type 1":
                    dmrs_grid[11, ::2] = 1
                else:
                    for sc in range(0, num_rbs_dmrs * 12, 6):
                        if sc < num_rbs_dmrs * 12 - 1:
                            dmrs_grid[11, sc:sc+2] = 1
            
            fig = go.Figure(data=go.Heatmap(
                z=dmrs_grid,
                colorscale=[[0, 'lightblue'], [1, 'red']],
                showscale=False
            ))
            
            # Add RB boundaries
            for rb in range(1, num_rbs_dmrs):
                fig.add_vline(x=rb*12-0.5, line_dash="dash", line_color="gray", opacity=0.3)
            
            fig.update_layout(
                title=f"DMRS Pattern - {dmrs_config_type}",
                xaxis_title="Subcarrier",
                yaxis_title="OFDM Symbol",
                height=500,
                yaxis=dict(autorange='reversed')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate overhead
            dmrs_res = np.sum(dmrs_grid)
            total_res = num_rbs_dmrs * 12 * num_symbols_dmrs
            overhead_pct = 100 * dmrs_res / total_res
            
            st.metric("DMRS Overhead", f"{overhead_pct:.1f}%")
    
    with tab2:
        st.markdown("### CSI-RS (Channel State Information Reference Signal)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Purpose:**
            - Channel quality measurement (CQI)
            - Beam management
            - Mobility measurements
            - L1-RSRP reporting
            
            **Key Features:**
            - Configurable density (1, 2, 4, 8, 12, 16, 24, 32 ports)
            - Periodic, aperiodic, or semi-persistent
            - Lower overhead than DMRS
            - Can be beamformed
            """)
            
            csi_rs_periodicity = st.selectbox(
                "Periodicity",
                ["5 ms", "10 ms", "20 ms", "40 ms", "80 ms", "160 ms"],
                index=1
            )
            
            csi_rs_ports = st.selectbox("Number of Ports", [1, 2, 4, 8, 12, 16, 32], index=2)
        
        with col2:
            st.markdown("#### CSI-RS Resource Mapping Example")
            
            # Simple CSI-RS pattern (sparse)
            csirs_grid = np.zeros((14, 12 * 10))
            
            # Sparse pattern - every 4th subcarrier, specific symbols
            csi_symbols = [5, 9]
            for sym in csi_symbols:
                csirs_grid[sym, ::4] = 1
            
            fig = go.Figure(data=go.Heatmap(
                z=csirs_grid,
                colorscale=[[0, 'lightgray'], [1, 'green']],
                showscale=False
            ))
            
            fig.update_layout(
                title="CSI-RS Pattern (Example)",
                xaxis_title="Subcarrier",
                yaxis_title="OFDM Symbol",
                height=400,
                yaxis=dict(autorange='reversed')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            csirs_res = np.sum(csirs_grid)
            st.info(f"CSI-RS uses {csirs_res} REs per slot (periodic)")
    
    with tab3:
        st.markdown("### SSB (SS/PBCH Block)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **SS/PBCH Block consists of:**
            1. **PSS** (Primary Synchronization Signal)
            2. **SSS** (Secondary Synchronization Signal)
            3. **PBCH** (Physical Broadcast Channel)
            4. **PBCH DMRS** (Reference signals for PBCH)
            
            **Purpose:**
            - Cell search and initial synchronization
            - Cell identification (Physical Cell ID)
            - Coarse time/frequency synchronization
            - Broadcast essential system info (MIB)
            """)
            
            ssb_frequency = st.selectbox(
                "SSB Frequency Range",
                ["sub-3 GHz (FR1 low)", "3-6 GHz (FR1 high)", "24-40 GHz (FR2)"],
                index=0
            )
            
            if "FR1" in ssb_frequency:
                max_ssb = 4 if "low" in ssb_frequency else 8
            else:
                max_ssb = 64
            
            ssb_pattern = st.selectbox("SSB Pattern", ["Case A", "Case B", "Case C", "Case D", "Case E"])
        
        with col2:
            st.markdown("#### SSB Structure (4 OFDM Symbols × 240 Subcarriers)")
            
            # SSB pattern
            ssb_grid = np.zeros((4, 240))
            
            # Symbol 0: PSS (127 subcarriers centered)
            ssb_grid[0, 56:183] = 2  # PSS
            
            # Symbol 1: PBCH + DMRS
            ssb_grid[1, :] = 1  # PBCH
            dmrs_mask_sym1 = (ssb_grid[1, :] == 1)
            ssb_grid[1, dmrs_mask_sym1 & ((np.arange(240) % 4) == 0)] = 3  # PBCH DMRS
            
            # Symbol 2: SSS (127 subcarriers centered) + PBCH
            ssb_grid[2, 56:183] = 4  # SSS
            ssb_grid[2, :56] = 1  # PBCH
            ssb_grid[2, 183:] = 1  # PBCH
            dmrs_mask_sym2 = (ssb_grid[2, :] == 1)
            ssb_grid[2, dmrs_mask_sym2 & ((np.arange(240) % 4) == 0)] = 3  # PBCH DMRS
            
            # Symbol 3: PBCH + DMRS
            ssb_grid[3, :] = 1  # PBCH
            dmrs_mask_sym3 = (ssb_grid[3, :] == 1)
            ssb_grid[3, dmrs_mask_sym3 & ((np.arange(240) % 4) == 0)] = 3  # PBCH DMRS
            
            fig = go.Figure(data=go.Heatmap(
                z=ssb_grid,
                colorscale=[
                    [0, 'white'],
                    [0.2, 'lightblue'],  # PBCH
                    [0.4, 'red'],         # PSS
                    [0.6, 'orange'],      # DMRS
                    [0.8, 'blue'],        # SSS
                    [1, 'blue']
                ],
                showscale=False
            ))
            
            fig.update_layout(
                title="SSB Block Structure",
                xaxis_title="Subcarrier (within SSB)",
                yaxis_title="Symbol",
                height=300,
                yaxis=dict(autorange='reversed')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Legend
            st.markdown("""
            🔴 **PSS** | 🔵 **SSS** | 🔵 **PBCH** | 🟠 **PBCH DMRS**
            """)
            
            st.info(f"""
            **SSB Periodicity:** 5, 10, 20, 40, 80, or 160 ms (configurable)
            
            **Max SSBs in burst:** {max_ssb} (depends on frequency range)
            
            **SSB bandwidth:** 240 subcarriers @ 15/30 kHz = 3.6/7.2 MHz
            """)
    
    with st.expander("📚 Theory: Reference Signals"):
        st.markdown("""
        ### Reference Signal Types in 5G NR
        
        | Type | Purpose | Domain | Overhead |
        |------|---------|--------|----------|
        | DMRS | Channel estimation for demodulation | Time-frequency | 5-20% |
        | CSI-RS | Channel quality measurement | Time-frequency | 1-5% |
        | PSS/SSS | Synchronization, cell ID | Time-frequency | Fixed (SSB) |
        | PTRS | Phase tracking (mmWave) | Time-frequency | 0-5% |
        | SRS | Uplink sounding | Frequency | Variable |
        
        ### DMRS (Demodulation Reference Signal)
        
        **Purpose:** Enable coherent demodulation of PDSCH/PUSCH
        
        **Key features:**
        - **UE-specific:** Different for each user
        - **Beamformed:** Follows data beam
        - **Two types:**
          - Type 1: Every other subcarrier (higher density)
          - Type 2: 2 out of 6 subcarriers (lower density)
        - **CDM groups:** Code Division Multiplexing for multi-layer MIMO
        - **Front-loaded:** Typically symbols 2-3 for early channel estimation
        - **Additional DMRS:** More symbols for high Doppler (mobility)
        
        **Overhead trade-off:**
        - More DMRS → Better channel estimation → Better demodulation
        - Less DMRS → More capacity for data → Higher throughput
        
        ### CSI-RS (Channel State Information Reference Signal)
        
        **Purpose:** UE measures channel quality and reports CSI
        
        **CSI includes:**
        - **CQI** (Channel Quality Indicator): Recommended MCS
        - **PMI** (Precoding Matrix Indicator): Recommended precoder
        - **RI** (Rank Indicator): Number of MIMO layers
        
        **Configurations:**
        - **Periodic:** Regular transmission, low signaling overhead
        - **Semi-persistent:** Activated/deactivated by MAC-CE
        - **Aperiodic:** Triggered by DCI, on-demand
        
        **Density:** Much sparser than DMRS (transmitted less frequently)
        
        ### SSB (SS/PBCH Block)
        
        **Purpose:** Initial access and cell search
        
        **Components:**
        1. **PSS (Primary Sync Signal):**
           - 3 possible sequences
           - Gives N_ID^(2) (0, 1, or 2)
           - First-stage synchronization
        
        2. **SSS (Secondary Sync Signal):**
           - 336 possible sequences
           - Gives N_ID^(1) (0 to 335)
           - Second-stage synchronization
           - Physical Cell ID = 3×N_ID^(1) + N_ID^(2) (0-1007)
        
        3. **PBCH (Physical Broadcast Channel):**
           - Carries MIB (Master Information Block)
           - Essential system information
           - SFN (System Frame Number), subcarrier spacing, etc.
        
        **SSB burst:**
        - Multiple SSBs transmitted in a burst
        - Each SSB can have different beam direction (beam sweeping)
        - FR1: Up to 4-8 SSBs
        - FR2: Up to 64 SSBs (massive beam sweeping for mmWave)
        
        **Periodicity:** Configurable 5-160 ms
        - More frequent → Faster cell search, more overhead
        - Less frequent → Lower overhead, slower initial access
        
        ### PTRS (Phase Tracking Reference Signal)
        
        **Purpose:** Track and compensate phase noise (mainly for mmWave)
        
        **Why needed at mmWave:**
        - Higher carrier frequency → More phase noise from oscillator
        - Phase noise destroys high-order modulation
        - PTRS allows tracking and correction
        
        **Configuration:**
        - Only for high-order modulation (64-QAM and above)
        - Configurable density based on modulation order
        - Time domain: Every few symbols
        - Frequency domain: Every few RBs
        
        ### SRS (Sounding Reference Signal)
        
        **Purpose:** Uplink channel sounding for gNB
        
        **Use cases:**
        - **Frequency-selective scheduling:** Find best RBs for UE
        - **Link adaptation:** Determine best MCS
        - **Beamforming:** Estimate uplink channel for precoding
        - **Timing advance:** Estimate propagation delay
        
        **Configuration:**
        - Periodic, semi-persistent, or aperiodic
        - Comb structure (transmit every Nth subcarrier)
        - Can cover full or partial bandwidth
        - UE-specific hopping pattern
        """)

# ============================================================================
# 5. TIME DOMAIN ANALYSIS
# ============================================================================
elif app_mode == "⏱️ Time Domain Analysis":
    st.markdown('<p class="section-header">⏱️ Time Domain Resource Allocation</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Configuration")
        
        scs_time = st.selectbox("Subcarrier Spacing (kHz)", [15, 30, 60, 120], index=1, key='time_scs')
        
        alloc_type = st.radio(
            "Allocation Type",
            ["Slot-based", "Non-slot-based", "Mini-slot"]
        )
        
        if alloc_type == "Non-slot-based":
            start_symbol = st.slider("Start Symbol", 0, 13, 2)
            duration_symbols = st.slider("Duration (symbols)", 1, 14-start_symbol, 10)
        elif alloc_type == "Mini-slot":
            mini_start = st.slider("Start Symbol", 0, 13, 0, key='mini_start')
            mini_duration = st.selectbox("Mini-slot Duration", [2, 4, 7])
        
        show_multiple_slots = st.checkbox("Show Multiple Slots", value=False)
        if show_multiple_slots:
            num_slots_show = st.slider("Number of Slots", 2, 10, 4)
    
    params_time = get_slot_params(scs_time)
    
    with col2:
        if not show_multiple_slots:
            st.markdown("### Single Slot Allocation")
            
            fig = go.Figure()
            
            symbols = list(range(14))
            
            if alloc_type == "Slot-based":
                # Full slot allocation
                allocation = [1.0] * 14
                colors = ['blue'] * 14
                title = "Slot-based Allocation (All 14 symbols)"
                
            elif alloc_type == "Non-slot-based":
                allocation = [0] * 14
                colors = ['lightgray'] * 14
                for i in range(start_symbol, start_symbol + duration_symbols):
                    if i < 14:
                        allocation[i] = 1.0
                        colors[i] = 'green'
                title = f"Non-slot Allocation (Symbols {start_symbol}-{start_symbol+duration_symbols-1})"
                
            else:  # Mini-slot
                allocation = [0] * 14
                colors = ['lightgray'] * 14
                for i in range(mini_start, mini_start + mini_duration):
                    if i < 14:
                        allocation[i] = 1.0
                        colors[i] = 'orange'
                title = f"Mini-slot ({mini_duration} symbols starting at {mini_start})"
            
            fig.add_trace(go.Bar(
                x=symbols,
                y=allocation,
                marker=dict(color=colors),
                showlegend=False
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title="OFDM Symbol",
                yaxis_title="Allocated",
                height=400,
                yaxis=dict(range=[0, 1.2])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate latency
            symbol_duration_us = params_time['slot_duration_ms'] * 1000 / 14
            
            if alloc_type == "Slot-based":
                latency_us = params_time['slot_duration_ms'] * 1000
                efficiency = 100.0
            elif alloc_type == "Non-slot-based":
                latency_us = duration_symbols * symbol_duration_us
                efficiency = 100.0 * duration_symbols / 14
            else:
                latency_us = mini_duration * symbol_duration_us
                efficiency = 100.0 * mini_duration / 14
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Latency", f"{latency_us:.1f} μs")
            with col_b:
                st.metric("Slot Efficiency", f"{efficiency:.1f}%")
            with col_c:
                st.metric("Symbols Used", f"{int(efficiency * 14 / 100)}/14")
        
        else:
            st.markdown(f"### Multiple Slots ({num_slots_show} slots)")
            
            # Create multi-slot visualization
            fig = go.Figure()
            
            total_symbols = num_slots_show * 14
            
            for slot_idx in range(num_slots_show):
                for sym_idx in range(14):
                    x_pos = slot_idx * 14 + sym_idx
                    
                    # Alternate pattern for visualization
                    if slot_idx % 2 == 0:
                        color = 'blue' if sym_idx < 12 else 'orange'  # Last 2 for UL
                    else:
                        color = 'lightblue' if sym_idx < 12 else 'lightyellow'
                    
                    fig.add_shape(
                        type="rect",
                        x0=x_pos-0.4, x1=x_pos+0.4,
                        y0=0, y1=1,
                        fillcolor=color,
                        line=dict(color='black', width=0.5)
                    )
                
                # Add slot separator
                if slot_idx < num_slots_show - 1:
                    fig.add_vline(x=(slot_idx+1)*14-0.5, line_dash="dash", line_color="red", line_width=2)
            
            fig.update_layout(
                title=f"{num_slots_show} Consecutive Slots ({num_slots_show * params_time['slot_duration_ms']:.2f} ms total)",
                xaxis_title="Symbol Index",
                yaxis_title="",
                height=300,
                showlegend=False,
                yaxis=dict(showticklabels=False)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            total_time_ms = num_slots_show * params_time['slot_duration_ms']
            st.info(f"Total duration: {total_time_ms:.3f} ms = {total_time_ms * 1000:.1f} μs")
    
    with st.expander("📚 Theory: Time Domain Allocation"):
        st.markdown("""
        ### Time Domain Resource Allocation (TDRA)
        
        5G NR provides flexible time domain scheduling unlike LTE's fixed 1 ms TTI.
        
        ### Allocation Types
        
        **1. Slot-based:**
        - Allocates entire slot (14 symbols)
        - Traditional approach, similar to LTE
        - Lower signaling overhead
        - Good for throughput-oriented services
        
        **2. Non-slot-based:**
        - Allocates arbitrary start symbol + duration
        - Flexible resource allocation
        - Can start at any symbol (0-13)
        - Duration: 1-14 symbols
        - Reduces latency for time-critical data
        
        **3. Mini-slot:**
        - Very short allocations (2, 4, or 7 symbols)
        - **URLLC** (Ultra-Reliable Low Latency)
        - Fast scheduling response
        - Can be used for preemption
        
        ### Latency Reduction
        
        **LTE:** Minimum 1 ms TTI
        **5G NR slot-based:** 0.125-1 ms (depends on numerology)
        **5G NR mini-slot:** As low as ~18 μs (2 symbols @ 120 kHz SCS)
        
        **Example:**
        - μ=3 (120 kHz SCS): Slot = 125 μs, Symbol ≈ 9 μs
        - 2-symbol mini-slot ≈ 18 μs
        - Enables <1 ms air interface latency for URLLC
        
        ### PDSCH Time Domain Resource Allocation
        
        Configured in RRC as a table of SLIV (Start and Length Indicator Value):
        
        **SLIV** encodes:
        - S: Start symbol (0-13)
        - L: Length in symbols (1-14)
        
        Formula: $SLIV = 14(L-1) + S$ if $(L-1) \\leq 7$
        
        **DCI** just signals an index to this table (low overhead).
        
        ### Symbol-level Flexibility Benefits
        
        **1. TDD Flexibility:**
        - Guard period can be just a few symbols
        - More efficient than slot-level switching
        
        **2. Preemption:**
        - URLLC can preempt eMBB mid-slot
        - eMBB gets DPI (Downlink Preemption Indication)
        - Retransmit only affected symbols
        
        **3. Mixed numerology:**
        - Different SCS across BWPs/carriers
        - Coexistence of services with different requirements
        
        **4. Cross-slot scheduling:**
        - Schedule PDSCH/PUSCH in future slot
        - K0/K2 offset (in slots)
        - Allows processing time for UE
        
        ### Processing Timeline
        
        **N1 / N2:** Processing time in symbols
        - **N1:** PDSCH reception → HARQ-ACK transmission
        - **N2:** DCI reception → PUSCH transmission
        
        Depends on:
        - UE capability (1 or 2)
        - Numerology (μ)
        - DL/UL timing
        
        **Example (μ=1, capability 1):**
        - N1 = 13 symbols
        - Receive PDSCH in slot n
        - Transmit ACK in slot n+2 at earliest
        
        ### Slot Aggregation
        
        **PDSCH/PUSCH can span multiple slots:**
        - Better coverage (longer transmission time)
        - Lower code rate (more robust)
        - Frequency hopping across slots
        - Typically for cell-edge UEs or coverage scenarios
        """)

# ============================================================================
# 6. TDD CONFIGURATION
# ============================================================================
elif app_mode == "🔧 TDD Configuration":
    st.markdown('<p class="section-header">🔧 TDD Configuration</p>', unsafe_allow_html=True)
    
    st.markdown("""
    **TDD (Time Division Duplex):** Uplink and downlink share the same frequency but use different time slots.
    5G NR TDD is highly flexible with configurable DL/UL patterns.
    """)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### TDD Pattern Configuration")
        
        tdd_periodicity_ms = st.selectbox(
            "TDD Pattern Periodicity",
            [0.5, 0.625, 1.0, 1.25, 2.0, 2.5, 5.0, 10.0],
            index=2
        )
        
        num_dl_slots = st.slider("Full DL Slots", 0, 10, 7)
        num_dl_symbols = st.slider("DL Symbols in Partial Slot", 0, 13, 10)
        
        num_ul_slots = st.slider("Full UL Slots", 0, 10, 2)
        num_ul_symbols = st.slider("UL Symbols in Partial Slot", 0, 13, 2)
        
        scs_tdd = st.selectbox("Subcarrier Spacing (kHz)", [15, 30, 60, 120], index=1, key='tdd_scs')
    
    params_tdd = get_slot_params(scs_tdd)
    
    # Calculate pattern
    slots_in_period = int(tdd_periodicity_ms / params_tdd['slot_duration_ms'])
    
    # Build slot pattern
    slot_pattern = []
    
    # Full DL slots
    for _ in range(num_dl_slots):
        slot_pattern.append('D')
    
    # Partial slot (if any DL or UL symbols)
    if num_dl_symbols > 0 or num_ul_symbols > 0:
        guard = 14 - num_dl_symbols - num_ul_symbols
        partial = f"D{num_dl_symbols}G{guard}U{num_ul_symbols}"
        slot_pattern.append('X')  # Mark as special/partial
    
    # Full UL slots
    for _ in range(num_ul_slots):
        slot_pattern.append('U')
    
    # Pad with flexible if needed
    while len(slot_pattern) < slots_in_period:
        slot_pattern.append('F')  # Flexible
    
    with col2:
        st.markdown("### TDD Pattern Visualization")
        
        # Visualize pattern
        fig = go.Figure()
        
        colors = {'D': 'blue', 'U': 'green', 'X': 'orange', 'F': 'lightgray'}
        color_list = [colors[s] for s in slot_pattern[:slots_in_period]]
        
        fig.add_trace(go.Bar(
            x=list(range(slots_in_period)),
            y=[1] * slots_in_period,
            marker=dict(color=color_list),
            showlegend=False,
            hovertemplate='Slot %{x}: %{text}<extra></extra>',
            text=slot_pattern[:slots_in_period]
        ))
        
        fig.update_layout(
            title=f"TDD Pattern ({tdd_periodicity_ms} ms period = {slots_in_period} slots)",
            xaxis_title="Slot Index",
            yaxis_title="",
            height=300,
            yaxis=dict(showticklabels=False, range=[0, 1.2])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show symbol-level detail for partial slot
        if num_dl_symbols > 0 or num_ul_symbols > 0:
            st.markdown("### Partial Slot Detail")
            
            fig2 = go.Figure()
            
            symbols_partial = []
            colors_partial = []
            
            # DL symbols
            for i in range(num_dl_symbols):
                symbols_partial.append(i)
                colors_partial.append('blue')
            
            # Guard symbols
            guard_count = 14 - num_dl_symbols - num_ul_symbols
            for i in range(num_dl_symbols, num_dl_symbols + guard_count):
                symbols_partial.append(i)
                colors_partial.append('yellow')
            
            # UL symbols
            for i in range(num_dl_symbols + guard_count, 14):
                symbols_partial.append(i)
                colors_partial.append('green')
            
            fig2.add_trace(go.Bar(
                x=symbols_partial,
                y=[1] * 14,
                marker=dict(color=colors_partial),
                showlegend=False
            ))
            
            fig2.update_layout(
                title=f"Partial Slot: {num_dl_symbols}D + {guard_count}G + {num_ul_symbols}U",
                xaxis_title="Symbol",
                yaxis_title="",
                height=250,
                yaxis=dict(showticklabels=False)
            )
            
            st.plotly_chart(fig2, use_container_width=True)
    
    # Calculate DL/UL ratio
    total_dl_symbols = num_dl_slots * 14 + num_dl_symbols
    total_ul_symbols = num_ul_slots * 14 + num_ul_symbols
    total_symbols = slots_in_period * 14
    
    dl_pct = 100 * total_dl_symbols / total_symbols
    ul_pct = 100 * total_ul_symbols / total_symbols
    guard_pct = 100 - dl_pct - ul_pct
    
    st.markdown("### Resource Distribution")
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        st.metric("DL Symbols", f"{total_dl_symbols}/{total_symbols}")
    with col_b:
        st.metric("UL Symbols", f"{total_ul_symbols}/{total_symbols}")
    with col_c:
        st.metric("DL/UL Ratio", f"{dl_pct:.1f}% / {ul_pct:.1f}%")
    with col_d:
        st.metric("Guard/Flexible", f"{guard_pct:.1f}%")
    
    # Show pattern string
    st.markdown("### Pattern String")
    pattern_str = ''.join(slot_pattern[:slots_in_period])
    st.code(pattern_str, language=None)
    
    st.markdown("""
    **Legend:**
    - **D**: Full downlink slot
    - **U**: Full uplink slot
    - **X**: Special/partial slot (DL + Guard + UL)
    - **F**: Flexible (can be DL or UL as needed)
    """)
    
    with st.expander("📚 Theory: TDD Configuration"):
        st.markdown("""
        ### TDD vs FDD
        
        **FDD (Frequency Division Duplex):**
        - Separate frequencies for UL and DL
        - Paired spectrum
        - Simultaneous UL/DL transmission
        - Better for coverage (continuous transmission)
        - Used in lower frequency bands
        
        **TDD (Time Division Duplex):**
        - Same frequency for UL and DL
        - Unpaired spectrum
        - Time-multiplexed UL/DL
        - Channel reciprocity (UL ≈ DL channel)
        - More spectrum globally available
        - Better beamforming (can use DL CSI for UL precoding)
        
        ### 5G NR TDD Configuration
        
        **Configured in SIB1** (System Information Block 1):
        - TDD-UL-DL-ConfigCommon
        - Pattern1 (mandatory)
        - Pattern2 (optional, for additional flexibility)
        
        **Parameters:**
        1. **Periodicity:** 0.5, 0.625, 1, 1.25, 2, 2.5, 5, 10 ms
        2. **nrofDownlinkSlots:** Number of full DL slots
        3. **nrofDownlinkSymbols:** DL symbols in partial slot
        4. **nrofUplinkSlots:** Number of full UL slots
        5. **nrofUplinkSymbols:** UL symbols in partial slot
        
        ### Slot Format
        
        Each slot can be:
        - **D:** All DL symbols
        - **U:** All UL symbols
        - **F:** Flexible (configured later, can be DL or UL)
        
        Special slot format: **DL - Guard - UL**
        
        ### Guard Period
        
        **Purpose:** Time for switching between DL and UL
        - RF retune time
        - Power ramping
        - Timing advance adjustment
        
        **Duration:**
        - Typically 1-3 OFDM symbols
        - Depends on cell size and hardware
        - Larger cells need longer guard
        - At 30 kHz SCS: 1 symbol ≈ 36 μs
        
        ### Common TDD Patterns
        
        **Pattern 1: DDDSU (4:1 DL heavy)**
        - 4 DL slots, 1 special, 0 UL
        - 80% DL, 14% UL, 6% guard
        - Good for FWA, video streaming
        
        **Pattern 2: DDDUU (3:2)**
        - 3 DL, 2 UL
        - 60% DL, 40% UL
        - Balanced for general use
        
        **Pattern 3: DSUUU (1:3 UL heavy)**
        - 1 DL, 1 special, 3 UL
        - 20% DL, 66% UL, 14% guard
        - Rare, for special UL-heavy scenarios
        
        ### Dynamic TDD
        
        **Group-Common PDCCH (GC-PDCCH):**
        - Signals slot format to multiple UEs
        - Overrides semi-static configuration
        - Enables traffic-adaptive TDD
        - Used for flexible slots ('F')
        
        **Benefits:**
        - Adapt to traffic asymmetry in real-time
        - Better spectral efficiency
        - Requires good inter-cell coordination (avoid interference)
        
        ### TDD Challenges
        
        **1. Cross-link Interference:**
        - Adjacent cells with different DL/UL timing
        - gNB-to-gNB interference (DL interferes with neighbor's UL)
        - UE-to-UE interference (UL interferes with neighbor's DL)
        - Mitigation: Synchronized networks, guard bands
        
        **2. Latency:**
        - Must wait for UL slot for feedback
        - Longer HARQ RTT than FDD
        - Mitigated by shorter slots (higher SCS)
        
        **3. Coverage:**
        - Less UL time → Harder for cell edge UEs
        - More retransmissions needed
        - Solved with UL slot aggregation, power boosting
        
        ### Massive MIMO and TDD
        
        **TDD advantage: Channel reciprocity**
        
        $H_{UL} = H_{DL}^T$ (in TDD with calibration)
        
        This means:
        - gNB learns DL channel from UL SRS
        - No need for massive DL CSI feedback
        - Enables large antenna arrays (64, 128, 256 elements)
        - Critical for beamforming at mmWave and massive MIMO
        
        **In FDD:**
        - Need codebook-based feedback
        - Limited CSI feedback (overhead)
        - Harder to scale to large arrays
        
        This is why **most 5G mid-band deployments use TDD**.
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>5G NR Frame Structure Visualizer</strong> | Built with Streamlit</p>
    <p>Explore slots, symbols, resource grids, and physical channels</p>
</div>
""", unsafe_allow_html=True)
