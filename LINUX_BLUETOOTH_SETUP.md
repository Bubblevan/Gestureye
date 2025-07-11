# Linuxϵͳ����ͨ������ָ��

## ��������

������Linuxϵͳ������projectӦ�ò��л�������ͨ��ģʽʱ�����ܻ������������⣺
1. �޷��Զ���ȡ����MAC��ַ
2. ����������ʱ��ʾ"socket������������"����������������
3. �޷����յ�dyn_gestures�ͻ��˷��͵�������Ϣ

## �������

### 1. ��ȡLinuxϵͳ����MAC��ַ

#### ����1: ʹ���ṩ�Ľű�
```bash
cd project
python get_linux_bluetooth_mac.py
```

#### ����2: �ֶ���ȡ
```bash
# ����1: ʹ��hciconfig
sudo hciconfig

# ����2: ʹ��bluetoothctl
bluetoothctl show

# ����3: ��ȡϵͳ�ļ�
cat /sys/class/bluetooth/hci0/address

# ����4: �鿴����ӿ�
ip link show | grep -i bluetooth
```

### 2. ����projectӦ��

�༭ `project/config.py` �ļ���
```python
# ͨ�ŷ�ʽ����
CONNECTION_TYPE = 'serial'  # ͨ��ģʽ��'socket' �� 'serial' (����)

# ��������
BLUETOOTH_MAC = "�������MAC��ַ"  # ����: "00:11:22:33:44:55"
BLUETOOTH_PORT = 4  # ����RFCOMM�˿�
BLUETOOTH_ENABLED = True  # �Ƿ�������������
```

### 3. ����dyn_gestures�ͻ���

�༭ `dyn_gestures/config.py` �ļ���
```python
CONNECTION_TYPE = 'serial'      # ����ģʽ��'socket' �� 'serial'
BLUETOOTH_MAC = 'projectӦ�õ�����MAC��ַ'  # ��project/config.py�е�BLUETOOTH_MACһ��
BLUETOOTH_PORT = 4              # ����RFCOMM�˿�
```

### 4. ��װ��Ҫ������

```bash
# ��װ����֧�ֿ�
pip install pybluez

# �������������󣬿�����Ҫ��װϵͳ����
sudo apt-get install libbluetooth-dev
sudo apt-get install python3-dev

# ����ĳЩLinux���а棬���ܻ���Ҫ
sudo apt-get install bluetooth libbluetooth-dev
```

### 5. ������������

```bash
# ������������
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# �����������״̬
sudo systemctl status bluetooth

# ȷ������������������
sudo hciconfig hci0 up
```

### 6. ������������

#### ����project������
```bash
cd project
python app.py
```

��UI�У�
1. ���"ͨ��" -> "�л�ͨ�ŷ�ʽ" -> ѡ��"Bluetooth"
2. ���"����������"
3. �鿴��־��Ӧ����ʾ"����RFCOMM�����������ɹ�"

#### ����dyn_gestures�ͻ���
```bash
cd dyn_gestures
python main.py
```

### 7. �����ų�

#### ����1: ��Ȼ��ʾ"socket������������"
**ԭ��**: ������������ʼ��ʧ�ܣ��Զ�������socketģʽ
**���**: 
1. ����Ƿ�װ��pybluez: `pip install pybluez`
2. ������������Ƿ�����: `sudo systemctl status bluetooth`
3. ��������������Ƿ�����: `sudo hciconfig`

#### ����2: �޷���ȡ����MAC��ַ
**���**: �ֶ�����MAC��ַ
1. ���� `python get_linux_bluetooth_mac.py` ��ȡMAC��ַ
2. ����ȡ����MAC��ַ���� `project/config.py` �� `BLUETOOTH_MAC` �ֶ�

#### ����3: ���ӱ��ܾ�
**ԭ��**: ����ǽ��Ȩ������
**���**:
```bash
# ���RFCOMM�˿��Ƿ�ռ��
sudo lsof -i :4

# ������������
sudo systemctl restart bluetooth

# �������Ȩ��
sudo usermod -a -G bluetooth $USER
```

#### ����4: �ͻ����޷�����
**����嵥**:
- [ ] project��dyn_gestures��CONNECTION_TYPE������Ϊ'serial'
- [ ] BLUETOOTH_MAC��ַ������ȷ
- [ ] BLUETOOTH_PORT�˿�һ�£�Ĭ��4��
- [ ] ����������������
- [ ] �����豸��������Χ��

### 8. ����ģʽ

������ϸ��־�����
```python
# ��project/core/socket_server.py��
self.debug_mode = True  # BluetoothServer��
```

### 9. ��֤����

ʹ���ṩ�Ĳ��Խű���֤��
```bash
cd project
python get_linux_bluetooth_mac.py
```

�ɹ����ú���Ӧ�ÿ�����
- projectӦ����ʾ"����RFCOMM�����������ɹ�"
- ��ʾ��������MAC��ַ
- dyn_gestures�ͻ����ܹ����Ӳ�������������

## ����������Ϣ���������

| ������Ϣ | ԭ�� | ������� |
|---------|------|----------|
| "ϵͳ��֧������RFCOMMЭ��" | δ��װpybluez | `pip install pybluez` |
| "������������ʼ��ʧ��" | ��������δ���� | `sudo systemctl start bluetooth` |
| "�޷���ȡ��������MAC��ַ" | �Զ����ʧ�� | �ֶ�����MAC��ַ |
| "���ӱ��ܾ�" | �˿ڱ�ռ�û�Ȩ�޲��� | �����������񣬼��Ȩ�� |

## ����֧��

�����Ȼ�������⣬���ṩ������Ϣ��
1. Linux���а�Ͱ汾
2. �����������ͺ�
3. �����Ĵ�����־
4. `python get_linux_bluetooth_mac.py` �������� 