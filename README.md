# OlimapiaAPP-IA

## Pipeline
```mermaid
graph LR;
    id1[ASG];
    id2[ORM];
    id3[OlimpiaAPP];

    id1-->id2;
    id2-->id3;
```
1. Answer Sheet Generator (ASG) we need to generate the template.
2. Optical Mark Recognition (OMR) extract the answers on the paper.
3. Send the information to OliampiaAPP.
