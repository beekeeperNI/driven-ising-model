# Reproducibility

The final PDF and 25-cell notebook are preserved research records. The extracted modules and period-scan script isolate the numerical method from interactive plotting and shared notebook globals.

## Recovered principal experiment

The script targets Figure 6 of the final paper. Its protocol is recovered from zero-based notebook cell 5: L=40, T=2, J=1, h0=0.5; periods 10,20,50,75,100,125,150,200,300 MCS; seeds 101,202,303,404,505; 30 cycles per run, discarding 10. The plotted observable is the mean absolute **trapezoidal** loop integral, averaged over retained cycles within each run and then across independent runs. Error bars are standard errors across runs, not across individual sweeps. The same seeds are reused across periods, so cross-period comparisons are paired.

The PDF names this observable and its error convention; its caption does not enumerate all settings. The source cell is therefore the recovered protocol, not a proof that every published pixel came from this exact execution. Original machine-readable Figure 6 measurements and its execution environment are not present on main. A new full run reproduces the recovered experiment, not a certified bitwise reproduction of the published data. No digitized or synthetic reference values are used.

More detailed execution instructions and check results accompany the extracted implementation.
