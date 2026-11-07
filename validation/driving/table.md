# Driven reliability and period scan

L=40, T=2, J=1, h0=0.5. Eight independent runs per initial mode. ± denotes pointwise approximate 95% run-mean intervals. All quantities per spin; work is signed field work.

| P | Initial mode | Discarded / retained cycles | Mean W ± 95% | Mean abs(Q) ± 95% | Targeted checks |
|---:|---|---:|---:|---:|---|
| 10 | random | 50 / 150 | 0.100162 ± 0.004334 | 0.849729 ± 0.038792 | inconclusive |
| 10 | all_up | 50 / 150 | 0.094720 ± 0.000899 | 0.872699 ± 0.002767 | inconclusive |
| 125 | random | 20 / 60 | 1.673893 ± 0.002909 | 0.029152 ± 0.002689 | supported |
| 125 | all_up | 20 / 60 | 1.672821 ± 0.001637 | 0.029941 ± 0.001457 | supported |
| 300 | random | 20 / 60 | 1.411910 ± 0.007010 | 0.017420 ± 0.001256 | supported |
| 300 | all_up | 20 / 60 | 1.413059 ± 0.004893 | 0.019772 ± 0.001777 | supported |

## Common pilot scan

The period comparison uses the same 20 discarded + 60 retained cycles at every P; P=10 extended results above are deliberately not substituted into this scan. Only P=10,125,300 also received an all-up comparison. Other statuses cover within-random-start window checks only.

| P | Signed W ± 95% | Legacy absolute area ± 95% | Mean abs(Q) ± 95% | Pilot checks |
|---:|---:|---:|---:|---|
| 10 | 0.110857 ± 0.019356 | 0.092474 ± 0.019296 | 0.745692 ± 0.204218 | inconclusive |
| 20 | 0.209508 ± 0.006103 | 0.194186 ± 0.006156 | 0.804056 ± 0.006449 | inconclusive |
| 50 | 0.910727 ± 0.010925 | 0.911238 ± 0.010969 | 0.238404 ± 0.025353 | inconclusive |
| 75 | 1.372989 ± 0.007168 | 1.375793 ± 0.007246 | 0.090310 ± 0.010356 | inconclusive |
| 100 | 1.632403 ± 0.005513 | 1.627693 ± 0.005257 | 0.037916 ± 0.003275 | supported (tested checks only) |
| 125 | 1.673893 ± 0.002909 | 1.662784 ± 0.003072 | 0.029152 ± 0.002689 | supported (tested checks only) |
| 150 | 1.653265 ± 0.004103 | 1.639677 ± 0.004238 | 0.024103 ± 0.002611 | supported (tested checks only) |
| 200 | 1.569553 ± 0.004057 | 1.555125 ± 0.004167 | 0.021217 ± 0.001388 | supported (tested checks only) |
| 300 | 1.411910 ± 0.007010 | 1.399305 ± 0.007093 | 0.017420 ± 0.001256 | supported (tested checks only) |

Both definitions peak at P=125 on the sampled grid. Paired differences use common seed identities across periods:

| Contrast | Signed work difference ± 95% |
|---|---:|
| W(125) − W(10) | 1.563035 ± 0.018975 |
| W(125) − W(75) | 0.300903 ± 0.005465 |
| W(125) − W(100) | 0.041489 ± 0.007331 |
| W(125) − W(150) | 0.020627 ± 0.004121 |
| W(125) − W(200) | 0.104340 ± 0.005230 |
| W(125) − W(300) | 0.261983 ± 0.008648 |
