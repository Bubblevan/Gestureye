# ����RFCOMMͨ�Ź�������ָ��

## ����

`project`����֧��ͨ������RFCOMMЭ���������`dyn_gestures`���������ݡ����������������Socket��Bluetoothͨ�ŷ�ʽ֮���޷��л���

## ��������

? **����������RFCOMM������ʵ��**
? **��dyn_gestures��ȫ����**  
? **UI�ж�̬�л�ͨ�ŷ�ʽ**
? **��ϸ��״̬��ʾ�ʹ�����**
? **��ƽ̨֧��**

## ϵͳҪ��

### Linuxϵͳ
```bash
# ��װ����������
sudo apt-get install bluetooth libbluetooth-dev

# ��װPython������
pip install pybluez
```

### Windowsϵͳ
```bash
# Windowsͨ����������֧�֣���������Ҫ����Ŀ�
pip install pybluez
# ����ʹ��Windows�ض���������
```

### macOSϵͳ
```bash
# macOS������Ҫ�ض���������
pip install pybluez
# ����ʹ��macOS�ض���������
```

## ���ò���

### 1. ����dyn_gestures

��`dyn_gestures/config.py`�����ã�
```python
CONNECTION_TYPE = 'serial'  # ��������ģʽ
BLUETOOTH_MAC = 'XX:XX:XX:XX:XX:XX'  # ��ѡ��ָ��MAC��ַ
BLUETOOTH_PORT = 4  # RFCOMM�˿ں�
```

### 2. ����project UI

1. ����projectӦ�ã�`python app.py`
2. ����˵�����"ͨ��"
3. ѡ��"�л�ͨ�ŷ�ʽ"
4. ȷ���л���Bluetoothģʽ
5. �������Ƽ��

### 3. ��֤����

ʹ���ṩ�Ĳ��Խű���֤�������ܣ�
```bash
cd project
python test_bluetooth.py
```

## ʹ������

### ������������ģʽ

1. **����projectӦ��**
   ```bash
   cd project
   python app.py
   ```

2. **�л�������ģʽ** (�����δ����)
   - �˵��� �� ͨ�� �� �л�ͨ�ŷ�ʽ
   - ѡ��"��"ȷ���л���Bluetooth

3. **�������Ƽ��**
   - ���"����Socket������" (���ڻ���������������)
   - �鿴״̬��ʾ"����RFCOMM�����������ɹ�"

4. **����dyn_gestures**
   ```bash
   cd dyn_gestures
   python main.py
   ```

5. **��֤����**
   - project UIӦ��ʾ"�ͻ���������"
   - ��ʼ������ƣ�Ӧ���ܿ������ݴ���

## ״̬���

### ͨ��״̬�鿴
- �˵��� �� ͨ�� �� ��ʾͨ��״̬
- ��ݼ���`Ctrl+S`

### ״̬��Ϣ������
- ��ǰͨ�ŷ�ʽ��Bluetooth (RFCOMM)
- ���״̬��������/��ֹͣ
- �����˿ڣ�RFCOMM�˿�4
- ���������X������
- ����֧�֣�������/δ��װ
- Э�飺����RFCOMMͨ��
- MAC��ַ���Զ���Ȿ��������

## �����ų�

### ��������

#### 1. "ϵͳ��֧������RFCOMMЭ��"
**���������**
```bash
# Linux
sudo apt-get install bluetooth libbluetooth-dev
pip install pybluez

# Windows/macOS
pip install pybluez
```

#### 2. "��������������ʧ��"
**����ԭ��**
- ����Ӳ��δ����
- �˿ڱ�ռ��
- Ȩ�޲���

**���������**
```bash
# �������״̬
sudo systemctl status bluetooth  # Linux

# ��������
sudo systemctl start bluetooth   # Linux

# ���˿�ռ��
sudo netstat -tlnp | grep :4     # Linux
```

#### 3. "dyn_gestures����ʧ��"
**����嵥��**
- [ ] dyn_gestures����Ϊ`CONNECTION_TYPE = 'serial'`
- [ ] project�л���Bluetoothģʽ
- [ ] ����������������
- [ ] ����ǽδ��ֹ����
- [ ] �����豸�ڷ�Χ��

### ����ģʽ

���õ���������鿴��ϸ��Ϣ��
```python
# ��core/socket_server.py������
self.debug_mode = True  # BluetoothServer��
```

### ��������

ʹ�����ò��Խű���
```bash
cd project
python test_bluetooth.py
```

## ����ϸ��

### Э����
- **Э����**: `AF_BLUETOOTH`
- **socket����**: `SOCK_STREAM`
- **Э��**: `BTPROTO_RFCOMM`
- **Ĭ�϶˿�**: 4
- **����**: UTF-8
- **���ݸ�ʽ**: JSON

### ������
```
dyn_gestures (Bluetooth Client)
    �� JSON hand gesture data
    �� RFCOMM protocol
    �� 
project (Bluetooth Server)
    �� Parse & process
    ��
UI Display & Action Execution
```

### ������
- ? ������Socketͨ����ȫ����
- ? �޷��л�����������Ӧ��
- ? ��ͬ���������ݸ�ʽ
- ? ��ͬ��UI�͹���

## �߼�����

### �Զ���˿�
�޸�`BluetoothServer`��ʼ��������
```python
# ��ui/threads/socket_gesture_receiver.py��
self.server = BluetoothServer(host="", port=6)  # ʹ�ö˿�6
```

### ָ��MAC��ַ
```python
# �󶨵��ض�����������
self.server = BluetoothServer(host="00:11:22:33:44:55", port=4)
```

### �����Ż�
```python
# �������Ӷ���
self.server_socket.listen(10)  # Ĭ��Ϊ5

# �������ջ�����
data = client_socket.recv(2048)  # Ĭ��Ϊ1024
```

## ֧���뷴��

��������������Ҫ����֧�֣��룺
1. ���ϵͳ����״̬
2. ���в��Խű�ȷ�Ϲ���
3. �鿴���������Ϣ
4. �ṩ��ϸ�Ĵ�����Ϣ��ϵͳ����

---

**ע��**: ����������Ҫϵͳ����Ӳ��֧�ֺ���Ӧ����������ĳЩ������������ܲ�֧���������ܡ� 