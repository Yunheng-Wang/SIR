## ✨ How to Use ?

### 1️⃣ Configure Environment (Linux / macOS)
1. **Clone the repository**
   ```bash
   git clone https://github.com/Yunheng-Wang/SIR.git
   cd SIR
   ```
2. **Create the virtual environment**
   ```bash
   python -m venv sir
   source sir/bin/activate
   pip install -r requirements.txt
   ```
### 2️⃣ Prepare Data
Place your network data files into the **`Networks/`** folder. Reference the example below:  
   ```bash
   SIR/
   ├── Networks/
   │   ├── aves-barn-swallow-contact-network/
   │   │   └── aves-barn-swallow-contact-network.txt
   │   ├── mammalia-voles-rob-trapping-26/
   │   │   └── mammalia-voles-rob-trapping-26.txt
   │   ├── ...
   │   └── ...
   └── ...
```

### 3️⃣ Run
Execute the main script to start the simulation:
```bash
python running.py
```
If you want to monitor CPU usage in real time, open another terminal and run:
```bash
sudo apt install btop   
btop 
```

## 📌 Network Collection List
Here we list some websites containing real-world networks. When all networks from a website are processed, the progress will be marked with ✅.  
          
| Website  | Progress |
|--------------------------------------------------------|---|
| http://www.diag.uniroma1.it/challenge9/download.shtml  |❌|





## 📌 Task List




