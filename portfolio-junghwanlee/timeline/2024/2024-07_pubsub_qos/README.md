# 📑 Research Note: July — MQTT Advanced Study & Local Broker Implementation

---

## 🔹 Process

### 1. MQTT Fundamentals
- Reviewed **Publish/Subscribe** architecture: Client ↔ Broker  
- **Broker**: message routing, QoS management, TLS/SSL security, clustering support  
- **Client**: publish, subscribe, QoS configuration  

### 2. QoS (Quality of Service) Levels
- **QoS 0**: At most once (fast, but possible message loss)  
- **QoS 1**: At least once (no loss, but duplicates possible)  
- **QoS 2**: Exactly once (highest reliability, higher overhead)  
- Documented typical use cases: sensor data, alert systems, financial transactions:contentReference[oaicite:0]{index=0}  

### 3. Broker Environment Experiments
- Tested **local LAN broker** on Raspberry Pi → communication without internet successful  
- Installed **Mosquitto** on Windows, configured firewall and ports  
- Verified pub-sub with `mosquitto_pub` and `mosquitto_sub` CLI (without Paho library):contentReference[oaicite:1]{index=1}  

### 4. Configuration & Operation
- Edited `mosquitto.conf`: port settings, logging, persistence  
- Enabled message persistence and log storage path  
- Tested anonymous connections (`allow_anonymous true`)  

### 5. Topic Structure Design
- Applied hierarchical topic naming for scalability and filtering  
- Examples:  
  - `sensors/temperature`  
  - `sensors/humidity`  
  - `home/livingroom/temperature`  
- Verified that topic structure improves **routing, scalability, and access control**:contentReference[oaicite:2]{index=2}  

---

## 🔹 Purpose
- Strengthen understanding of **MQTT architecture, QoS, and Broker/Client roles**  
- Demonstrate that **local network communication is possible without internet**  
- Build a practical foundation with Mosquitto configuration and CLI-based pub-sub tests  
- Design scalable and secure topic structures for real-world IoT/industry scenarios  

---

## 🔹 Results
- Summarized differences and trade-offs across **QoS 0/1/2**  
- Successfully validated **local LAN communication** with Raspberry Pi broker  
- Confirmed **pub-sub operation** on Windows Mosquitto without Paho  
- Showed that **topic hierarchy** enhances scalability and message management  

---

## 🔹 Next Steps
- Benchmark QoS levels (latency, loss rate, duplication)  
- Test hybrid setup: local broker + cloud broker integration  
- Practice **TLS/SSL security** for MQTT communication  
- Define **topic naming conventions** for industrial IoT data  

---

## 📚 References
- MQTT 5.0 Protocol & QoS Overview:contentReference[oaicite:3]{index=3}  
- Mosquitto official docs (Windows/Linux installation & configuration)  
- EMQX Blog: Introduction to MQTT QoS  
- Broker Comparison: Mosquitto, HiveMQ, EMQ X:contentReference[oaicite:4]{index=4}  
