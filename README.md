# Awesome-Software-Supply-Chain-Security
This repository collects and organizes academic papers related to Software Supply Chain research, focusing on works published in the Top 4 Software Engineering Conferences (ICSE, FSE, ASE, ISSTA) and the Top 4 Security Conferences (IEEE S&P, ACM CCS, NDSS, USENIX Security).

## Research Papers (2023-2025)

### Security Conferences (Big 4)

#### 2025

##### USENIX Security

- ChainFuzz: Exploiting Upstream Vulnerabilities in Open-Source Supply Chains
  - [Paper](https://www.usenix.org/conference/usenixsecurity25/presentation/deng) | [PDF](https://www.usenix.org/system/files/usenixsecurity25-deng.pdf)

- An industry interview study of software signing for supply chain security
  - [Paper](https://www.usenix.org/conference/usenixsecurity25/presentation/kalu) | [PDF](https://www.usenix.org/system/files/usenixsecurity25-kalu.pdf)

##### NDSS

- Attributing Open-Source Contributions is Critical but Difficult: A Systematic Analysis of GitHub Practices and Their Impact on Software Supply Chain Security
  - [Paper](https://www.ndss-symposium.org/wp-content/uploads/2025-613-paper.pdf) | [DOI](https://doi.org/10.60882/cispa.28714826.v1) | [Slides](https://www.ndss-symposium.org/wp-content/uploads/9D-f0613-holtgrave.pdf)

#### 2024

##### IEEE S&P (Oakland)

- Signing in four public software package registries: Quantity, quality, and influencing factors
  - [Paper](https://ieeexplore.ieee.org/abstract/document/10646801/)

##### USENIX Security

- iHunter: Hunting Privacy Violations at Scale in the Software Supply Chain on iOS
  - [Paper](https://www.usenix.org/conference/usenixsecurity24/presentation/liu-dexin)

#### 2023

##### IEEE S&P (Oakland)

- SoK: Taxonomy of Attacks on Open-Source Software Supply Chains
  - [Paper](https://ieeexplore.ieee.org/abstract/document/10179304) | [DOI](https://doi.org/10.1109/SP46215.2023.10179304)

- It's like flossing your teeth: On the importance and challenges of reproducible builds for software supply chain security
  - [Paper](https://ieeexplore.ieee.org/abstract/document/10179320) | [DOI](https://doi.org/10.1109/SP46215.2023.10179320)

- "Always Contribute Back": A Qualitative Study on Security Challenges of the Open Source Supply Chain
  - [Paper](https://ieeexplore.ieee.org/document/10179378) | [DOI](https://doi.org/10.1109/SP46215.2023.10179378)

- Continuous intrusion: Characterizing the security of continuous integration services
  - [Paper](https://ieeexplore.ieee.org/abstract/document/10179471) | [DOI](https://doi.org/10.1109/SP46215.2023.10179471)

##### USENIX Security

- V1SCAN: Discovering 1-day Vulnerabilities in Reused C/C++ Open-source Software Components Using Code Classification Techniques
  - [Paper](https://www.usenix.org/conference/usenixsecurity23/presentation/woo) | [PDF](https://www.usenix.org/system/files/usenixsecurity23-woo.pdf)

- Beyond typosquatting: an in-depth look at package confusion
  - [Paper](https://www.usenix.org/conference/usenixsecurity23/presentation/neupane) | [PDF](https://www.usenix.org/system/files/usenixsecurity23-neupane.pdf)

- Union under duress: Understanding hazards of duplicate resource mismediation in android software supply chain
  - [Paper](https://www.usenix.org/conference/usenixsecurity23/presentation/wang-xueqiang-duress) | [PDF](https://www.usenix.org/system/files/usenixsecurity23-wang-xueqiang-duress.pdf)

---

### Software Engineering Conferences (Big 4)

#### 2025

##### ICSE

- ZTDJAVA: Mitigating Software Supply Chain Vulnerabilities via Zero-Trust Dependencies
  - [Paper](https://doi.org/10.1109/ICSE55347.2025.00148)

##### FSE/ESEC

- Dirty-Waters: Detecting Software Supply Chain Smells
  - [Paper](https://doi.org/10.1145/3696630.372857) | [PDF](https://dl.acm.org/doi/pdf/10.1145/3696630.3728578)

##### ASE

- Propagation-Based Vulnerability Impact Assessment for Software Supply Chains
  - [Paper](https://arxiv.org/pdf/2506.01342)

#### 2024

##### ICSE

- Strengthening supply chain security with fine-grained safe patch identification
  - [Paper](https://dl.acm.org/doi/abs/10.1145/3597503.3639104) | [PDF](https://dl.acm.org/doi/pdf/10.1145/3597503.3639104)

##### ASE

- Software Supply Chain Risk: Characterization, Measurement & Attenuation
  - [Paper](https://dl.acm.org/doi/pdf/10.1145/3691620.3695608)

- Towards robust detection of open source software supply chain poisoning attacks in industry environments
  - [Paper](https://dl.acm.org/doi/abs/10.1145/3691620.3695262) | [PDF](https://dl.acm.org/doi/pdf/10.1145/3691620.3695262)

#### 2023

##### FSE/ESEC

- Modeling the Centrality of Developer Output with Software Supply Chains
  - [Paper](https://dl.acm.org/doi/pdf/10.1145/3611643.3613873)

---

## Statistics

| Conference | 2025 | 2024 | 2023 | Total |
|------------|------|------|------|-------|
| Security |
| IEEE S&P | 0 | 1 | 4 | 5 |
| USENIX Security | 2 | 1 | 3 | 6 |
| ACM CCS | 0 | 0 | 0 | 0 |
| NDSS | 1 | 0 | 0 | 1 |
| Software Engineering |
| ICSE | 1 | 1 | 0 | 2 |
| FSE/ESEC | 1 | 0 | 1 | 2 |
| ASE | 1 | 2 | 0 | 3 |
| ISSTA | 0 | 0 | 0 | 0 |
| Total | 6 | 5 | 8 | 19 |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. When adding papers, please follow the format above and include:

- Full paper title
- Links to paper, code (if available), and slides (if available)

### Commit Message Format

Please use the following format for commit messages:

```
[Conference Year] Add/Update paper title
```

Examples:
- `[ICSE 2025] Add paper on supply chain vulnerability detection`
- `[CCS 2024] Add malicious package detection research`
- `[FSE 2023] Update paper links`
- `[Multiple] Add 3 papers from S&P and NDSS 2024`

Format guidelines:
- Use the conference abbreviation (ICSE, FSE, ASE, ISSTA, S&P, CCS, NDSS, USENIX Security)
- Include the year
- Use "Add" for new papers, "Update" for modifications
- Keep the message concise but descriptive
- For multiple papers from different conferences, use `[Multiple]`
