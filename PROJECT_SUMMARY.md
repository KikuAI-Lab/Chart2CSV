# Chart2CSV - Project Summary

## 📊 Overview

**Chart2CSV** - CLI-first plot digitizer that extracts data from chart images (PNG/JPG/PDF) to CSV/JSON with honest confidence scoring and calibration fallback.

**Status:** MVP Ready for Development
**Timeline:** 7-10 days solo development
**License:** MIT
**Language:** Python 3.8+

## 🎯 Core Value Proposition

1. **Honest** - Never gives wrong data silently, always reports confidence
2. **Fast** - Seconds vs minutes/hours of manual work
3. **Private** - Offline-first, no network required
4. **Fallback** - Manual calibration when auto fails (15-30 seconds)
5. **Proof** - Overlay visualization for verification

## 🏗️ Architecture

### CLI-First Strategy
- **Core:** Pure CV/OCR library (`chart2csv.core`)
- **CLI:** Command-line interface (`chart2csv.cli`)
- **API:** Thin wrapper layer (Iteration 2, 1-3 days to add)

### Tech Stack
- **CV:** OpenCV
- **OCR:** Tesseract (Apache 2.0)
- **PDF:** pypdfium2 (Apache 2.0 / BSD-3)
- **Framework:** Python, NumPy, SciPy

## 📁 Project Structure

```
Chart2CSV/
├── README.md                    # Main documentation
├── QUICKSTART.md               # 5-minute setup guide
├── requirements.txt            # Dependencies
├── setup.py                    # Package setup
│
├── chart2csv/
│   ├── core/                   # Pure CV/OCR logic
│   │   ├── pipeline.py         # Main: extract_chart()
│   │   ├── preprocess.py       # Image cleanup
│   │   ├── detection.py        # Axes, ticks, plot area
│   │   ├── ocr.py              # Tesseract wrapper
│   │   ├── transform.py        # Pixel→value mapping
│   │   ├── export.py           # CSV/JSON/overlay
│   │   └── types.py            # Data structures
│   │
│   ├── cli/                    # CLI interface
│   │   ├── main.py             # Entry point
│   │   ├── calibrate.py        # Interactive calibration
│   │   └── batch.py            # Batch processing
│   │
│   └── tests/                  # Unit tests
│
├── docs/
│   ├── MVP_ROADMAP.md          # Day-by-day 7-10 day plan
│   ├── BENCHMARK_PLAN.md       # Testing strategy
│   └── ARCHITECTURE.md         # Technical design (TODO)
│
├── fixtures/                   # Benchmark dataset (30-50 images)
├── scripts/                    # Benchmark runner
└── examples/                   # Usage examples
```

## 🚀 MVP Scope (v0.1.0)

### Supported (12 Features)
1. PNG/JPG input
2. 3 chart types: scatter, line (single), bar
3. Auto-detect plot area + manual `--crop`
4. Auto-detect axes + manual `--x-axis`/`--y-axis`
5. OCR tick labels (Tesseract)
6. Linear scale only
7. CSV export
8. JSON metadata
9. Overlay generation
10. Confidence scoring (0-1)
11. Warning system (12 codes)
12. Calibration fallback

### Not Supported (Roadmap)
- Multi-series + legend parsing
- Dual-axis charts
- Auto log-scale detection
- Click-based calibration UI
- PDF multi-page auto
- Batch parallelization
- Web UI / API / Telegram

## 📊 Success Metrics

### Quality (30-50 fixture benchmark)
- Success without calibration: ≥40% (stretch: ≥60%)
- Clean fixtures success: ≥70% (stretch: ≥80%)
- Hard cases: ≥20% (validation of fallback)
- OCR tick success rate: ≥60%
- Median runtime: <2 seconds
- **No silent failures** (always warn when uncertain)

### Developer Experience
- `pip install chart2csv` works (with Tesseract installed)
- Clear error messages
- Overlay always generated
- Warnings map to specific fixes

## 💰 Monetization Strategy

### Free Tier (Open Source)
- PNG single file
- Basic chart types
- Core features

### Pro License ($29-99 or $9-19/month)
- PDF pages
- Batch folders
- Advanced overlay
- Benchmark mode
- Priority support

### Enterprise
- Self-contained binary
- On-premise deployment
- Custom training

## ⏱️ Development Timeline

### Week 1 (Days 1-7): MVP Core
- Day 1-2: Preprocess + plot area detection
- Day 3: Axis detection
- Day 4-5: OCR tick labels (RISKY)
- Day 6: Transform + calibration
- Day 7: Data extraction (scatter, line, bar)

### Week 2 (Days 8-10): Polish
- Day 8: Export + overlay
- Day 9: Confidence + warnings
- Day 10: Batch + benchmark + docs

### Iteration 1 (Weeks 2-3)
- Click-based calibration UI
- PDF multi-page
- Improved OCR preprocessing
- Grid removal option
- Batch parallelization

### Iteration 2 (Weeks 4-5)
- Log-scale auto-detection
- Multi-series (beta)
- Legend parsing (beta)
- API wrapper (FastAPI)

## 🎲 Risk Assessment

### High Risk, High Impact
- **OCR fails on >50% fixtures** → Mitigated by calibration fallback
- **Log-scale silent failures** → Mitigated by warning system

### Medium Risk
- **Line extraction quality** → Start with scatter/bar, iterate
- **Grid interference** → Optional `--remove-grid`
- **Low resolution inputs** → Warning + suggest higher res

### Controlled
- **Installation friction** → Clear docs, consider binary later
- **User expectations** → "Best-effort + calibration", not "perfect auto"

## 📚 Key Documents

1. [README.md](README.md) - Main documentation, usage examples
2. [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
3. [MVP_ROADMAP.md](docs/MVP_ROADMAP.md) - Day-by-day implementation plan
4. [BENCHMARK_PLAN.md](docs/BENCHMARK_PLAN.md) - Testing strategy

## 🔧 Next Steps

### For Development
1. Set up dev environment
2. Collect initial 30 fixtures
3. Implement Day 1-2 (preprocess + crop detection)
4. Test on real images early and often
5. Build calibration fallback before perfecting auto

### For Users (Post-MVP)
1. Install: `pip install chart2csv`
2. Try: `chart2csv plot.png --overlay check.png`
3. Verify: Open `check.png` to see extraction
4. Use: `data.csv` for analysis

## 💡 Key Insights from Design

### Product
- **Honesty > Perfection** - Better to warn than fail silently
- **Fallback is feature** - Calibration, not bug
- **Privacy wins** - Offline-first attracts compliance users
- **Overlay = trust** - Visual proof builds confidence

### Technical
- **CLI-first = focus** - Avoid infrastructure rabbit hole
- **OCR is hard** - Plan for failure, not success
- **Best-effort auto** - Don't promise what CV can't deliver
- **Manual overrides** - Expert users need control

### Monetization
- **CLI sells without SaaS** - License model viable
- **Open core** - Free basic, paid advanced
- **Enterprise offline** - Compliance premium

## 📞 Contact

- **Issues:** https://github.com/yourusername/chart2csv/issues
- **Discussions:** https://github.com/yourusername/chart2csv/discussions
- **Email:** your.email@example.com

---

**Built with the philosophy: "Better to say 'not sure' than give wrong data silently."**

**Privacy-first. Offline-capable. Honest always.**
