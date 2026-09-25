# Polyglot tools for Supreme Food Industry

This folder keeps small helpers in multiple languages. The live site runs on
**HTML + CSS + JS + Python (Flask)**. Other languages are included as real,
runnable companions for deploy flexibility and demos.

| Lang | Path | Role |
|------|------|------|
| HTML/CSS/JS | `../` | Frontend |
| Python | `python/rice_calc.py` + `../server.py` | Backend API |
| PHP | `php/contact.php` | Alternate contact endpoint (Apache) |
| C | `c/rice_calc.c` | Native bag calculator |
| C++ | `cpp/rice_calc.cpp` | Native bag calculator |
| Java | `java/RiceCalc.java` | Bag calculator source |

## Build native calculators

```bash
gcc -O2 -o ../../bin/rice_calc_c c/rice_calc.c
g++ -O2 -o ../../bin/rice_calc_cpp cpp/rice_calc.cpp
# if JDK available:
javac -d ../../bin java/RiceCalc.java
```

Flask `/api/calc?bags=10` prefers the C++ binary, then C, then Python.
