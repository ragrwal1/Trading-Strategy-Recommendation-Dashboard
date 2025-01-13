<script lang="ts">
    import { onMount } from 'svelte';
    import Card from '../components/Card.svelte';
  
    const API_DOMAIN = 'http://127.0.0.1:8000';
  
    let ticker: string = 'NVDA';
    let risk_free_rate: string = '0.05';
    let max_expiries: string = '3';
    let min_volume: string = '10';
    let min_open_interest: string = '10';
    let results_limit: string = '10';
    let max_strike_diff: string = '20';
    let min_cost_debit: string = '2.0';
    let max_short_strike: string = '142.5';
  
    let diagnosticsData: Record<string, any> | null = null;
    let bullCallSpreadsData: any[] = [];
    let isLoading: boolean = false;
    let errorMessage: string = '';
  
    async function fetchData() {
      isLoading = true;
      errorMessage = '';
      try {
        const diagRes = await fetch(`${API_DOMAIN}/diagnostics?ticker=${ticker}`);
        if (!diagRes.ok) {
          throw new Error(`Failed to fetch diagnostics: ${diagRes.statusText}`);
        }
        diagnosticsData = await diagRes.json(); 
  
        let bullUrl = `${API_DOMAIN}/bull_call_spreads?`;
        bullUrl += `ticker=${ticker}&risk_free_rate=${risk_free_rate}&max_expiries=${max_expiries}`;
        bullUrl += `&min_volume=${min_volume}&min_open_interest=${min_open_interest}`;
        bullUrl += `&results_limit=${results_limit}&max_strike_diff=${max_strike_diff}`;
        bullUrl += `&min_cost_debit=${min_cost_debit}&max_short_strike=${max_short_strike}`;
  
        const bullRes = await fetch(bullUrl);
        if (!bullRes.ok) {
          throw new Error(`Failed to fetch spreads: ${bullRes.statusText}`);
        }
        bullCallSpreadsData = await bullRes.json();
      } catch (error) {
        errorMessage = (error as Error).message;
      } finally {
        isLoading = false;
      }
    }
  
    onMount(() => {
      fetchData();
    });
  </script>
  
  <div class="dashboard">
    <div class="main-content">
      <h1>Bull Call Spreads</h1>
  
      {#if isLoading}
        <p class="loading">Loading...</p>
      {/if}
  
      {#if errorMessage}
        <p class="error">{errorMessage}</p>
      {/if}
  
      <!-- Diagnostics Panel -->
      {#if diagnosticsData}
        <Card size="large" shape="rounded" styles="margin-bottom: 1.5rem;">
          <h2 class="card-title">Diagnostics</h2>
          {#each Object.entries(diagnosticsData) as [key, value]}
            <p class="diagnostic-entry"><strong>{key}:</strong> {value}</p>
          {/each}
        </Card>
      {/if}
  
      <!-- Spread Data -->
      {#if bullCallSpreadsData.length > 0}
        <Card size="large" shape="rounded" stack styles="margin-bottom: 1rem;">
          <div class="spread-header">
            <span>Long Strike</span>
            <span>Short Strike</span>
          </div>
          <div class="spread-info">
            <span>Cost Long</span>
            <span>Cost Short</span>
            <span>Cost Debit</span>
            <span>Max Profit</span>
            <span>Max Loss</span>
            <span>Risk Reward</span>
            <span>Long IV</span>
            <span>Short IV</span>
            <span>Spread Delta</span>
            <span>Spread Gamma</span>
            <span>Spread Theta</span>
            <span>Spread Vega</span>
            <span>Expiration</span>
          </div>
        </Card>
  
        {#each bullCallSpreadsData as spread}
          <Card size="medium" shape="rounded" stack>
            <div class="spread-header">
              <span>{spread.long_strike}</span>
              <span>{spread.short_strike}</span>
            </div>
            <div class="spread-info">
              <span>{spread.cost_long}</span>
              <span>{spread.cost_short}</span>
              <span>{spread.cost_debit}</span>
              <span>{spread.max_profit}</span>
              <span>{spread.max_loss}</span>
              <span>{spread.risk_reward}</span>
              <span>{spread.long_iv}</span>
              <span>{spread.short_iv}</span>
              <span>{spread.spread_delta}</span>
              <span>{spread.spread_gamma}</span>
              <span>{spread.spread_theta}</span>
              <span>{spread.spread_vega}</span>
              <span>{spread.expiration}</span>
            </div>
          </Card>
        {/each}
      {/if}
    </div>
  
    <!-- Configurations -->
    <div class="config-tab">
      <h2>Configurations</h2>
  
      <Card size="small" shape="rounded" styles="padding: 1.5rem;">
        <div class="config-item">
          <label for="ticker">Ticker:</label>
          <input id="ticker" type="text" bind:value={ticker} placeholder="e.g. NVDA" />
        </div>
  
        <div class="config-item">
          <label for="risk_free_rate">Risk Free Rate:</label>
          <input id="risk_free_rate" type="text" bind:value={risk_free_rate} placeholder="0.05" />
        </div>
  
        <div class="config-item">
          <label for="max_expiries">Max Expiries:</label>
          <input id="max_expiries" type="text" bind:value={max_expiries} placeholder="3" />
        </div>
  
        <div class="config-item">
          <label for="min_volume">Min Volume:</label>
          <input id="min_volume" type="text" bind:value={min_volume} placeholder="10" />
        </div>
  
        <div class="config-item">
          <label for="min_open_interest">Min Open Interest:</label>
          <input id="min_open_interest" type="text" bind:value={min_open_interest} placeholder="10" />
        </div>
  
        <div class="config-item">
          <label for="results_limit">Results Limit:</label>
          <input id="results_limit" type="text" bind:value={results_limit} placeholder="10" />
        </div>
  
        <div class="config-item">
          <label for="max_strike_diff">Max Strike Diff:</label>
          <input id="max_strike_diff" type="text" bind:value={max_strike_diff} placeholder="20" />
        </div>
  
        <div class="config-item">
          <label for="min_cost_debit">Min Cost Debit:</label>
          <input id="min_cost_debit" type="text" bind:value={min_cost_debit} placeholder="2.0" />
        </div>
  
        <div class="config-item">
          <label for="max_short_strike">Max Short Strike:</label>
          <input id="max_short_strike" type="text" bind:value={max_short_strike} placeholder="142.5" />
        </div>
  
        <button on:click={fetchData}>Refresh</button>
      </Card>
    </div>
  </div>
  
  <style>
    :global(html, body) {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: radial-gradient(circle at center, #434371, #363636);
      color: #ffffff;
      height: 100%;
    }
  
    .dashboard {
      display: flex;
      flex-wrap: wrap;
      gap: 1.5rem;
      padding: 2rem;
    }
  
    .main-content {
      flex: 2;
      min-width: 60%;
    }
  
    .config-tab {
      flex: 1;
      min-width: 30%;
      background: rgba(255, 255, 255, 0.05);
      padding: 1rem;
      border-radius: 8px;
    }
  
    .card-title {
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }
  
    .diagnostic-entry {
      margin: 0.5rem 0;
    }
  
    .spread-header {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      font-weight: bold;
      text-transform: uppercase;
      margin-bottom: 1rem;
    }
  
    .spread-info {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
      gap: 1rem;
    }
  
    label {
      font-weight: bold;
    }
  
    input {
      padding: 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: 4px;
      color: #fff;
    }
  
    button {
      background-color: #1e90ff;
      border: none;
      color: #fff;
      padding: 0.5rem 1rem;
      cursor: pointer;
      border-radius: 4px;
      transition: background-color 0.2s;
    }
  
    button:hover {
      background-color: #1a78d5;
    }
  
    .loading {
      color: #1e90ff;
      font-weight: bold;
    }
  
    .error {
      color: #ff6961;
      font-weight: bold;
    }
  </style>