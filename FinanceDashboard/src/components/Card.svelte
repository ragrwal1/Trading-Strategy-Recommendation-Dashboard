<script lang="ts">
    export let size: string = 'medium'; // small, medium, large
    export let shape: string = 'rounded'; // rounded, square, etc.
    export let stack: boolean = false; // Enable stacking
    export let styles: string = ''; // Custom styles
  </script>
  
  <div
    class={`card ${size} ${shape} ${stack ? 'stacked' : ''}`}
    style={styles}
  >
    <slot></slot>
  </div>
  
  <style>
    .card {
      background: rgba(255, 255, 255, 0.07);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 1rem;
      margin: 0.5rem 0;
      transition: all 0.1s ease;
    }
  
    .card:hover {
      transform: translateY(-2px);
    transform: translateY(-2px) scale(1.02);
      background: rgba(255, 255, 255, 0.08);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2), inset 0 0 30px rgba(255, 255, 255, 0.04);
    }
  
    /* Size styles */
    .small {
      padding: 0.5rem;
    }
  
    .medium {
      padding: 1rem;
    }
  
    .large {
      padding: 1.5rem;
    }
  
    /* Shape styles */
    .rounded {
      border-radius: 1px;
    }
  
    .square {
      border-radius: 0;
    }
  
    /* Stacked style */
    .stacked {
      margin-bottom: 0;
    }
  </style>