# �������ƴ��书��ʹ��ָ��

## ����

����Ŀʵ�����������������ƴ���ϵͳ��֧�ִ���ݮ�ɵ�PC��ʵʱ�������ݴ��䡣ϵͳ����21���ֲ��ؼ������������ʶ�����Ĵ��䡣

## ?? ϵͳ�ܹ�

```
��ݮ�ɶ� (������)          PC�� (������)
��������������������������������������       ��������������������������������������
��   ���Ƽ��      ��       ��   ����������    ��
��   ��             ��       ��   ��             ��
��   ���ݴ��      �� ====> ��   ���ݽ��      ��
��   ��             ��  ����  ��   ��             ��
��   ��������      ��       ��   ����ִ��      ��
��������������������������������������       ��������������������������������������
```

## ? �������

### 1. ����Э�� (`bluetooth/protocol.py`)
- **���ݰ�����**���ֲ��ؼ��㡢���ƽ����������ݡ�������
- **���ݸ�ʽ**��������ͷ�� + JSON�غ� + У���
- **���ݽṹ**��`HandData`��`GestureData`

### 2. ���������� (`bluetooth/sender.py`)
- **��;**����ݮ�ɶ˷�������
- **����**���Զ����������Ͷ��С���������

### 3. ���������� (`bluetooth/receiver.py`)
- **��;**��PC�˽�������
- **����**��������ģʽ��Qt�źż��ɡ����ӹ���

### 4. ���������� (`bluetooth/manager.py`)
- **��;**��ϵͳ���ɺͶ���ִ��
- **����**���Զ����Ƽ�⡢������

## ? ���ٿ�ʼ

### ����Ҫ��

**PC�ˣ�**
```bash
pip install PyQt6 opencv-python cvzone mediapipe numpy pynput pywin32 pybluez
```

**��ݮ�ɶˣ�**
```bash
pip install opencv-python cvzone mediapipe numpy pybluez
```

### ����ʹ������

#### 1. PC�ˣ���������

```python
from bluetooth.manager import BluetoothManager

# ��������������
bt_manager = BluetoothManager()

# ��������������
bt_manager.start_bluetooth_server()

# �����źŴ���
bt_manager.bluetooth_gesture_detected.connect(lambda name, hand, conf: 
    print(f"��⵽����: {name} ({hand}��, {conf:.1f}%)"))
```

#### 2. ��ݮ�ɶˣ���������

```python
from bluetooth.raspberry_pi_sender import RaspberryPiGestureSender

# �������������滻ΪPC��������ַ��
sender = RaspberryPiGestureSender("PC_BLUETOOTH_ADDRESS")

# ���ӵ�PC
if sender.connect_to_pc():
    # ��ʼ���Ƽ��ͷ���
    sender.start_gesture_detection_and_send()
```

## ? Э�����

### ���ݰ���ʽ

```
+--------+--------+------+------+----------+--------+----------+----------+--------+
| Header | Version| Type | Seq  | Length   | Payload (JSON)    | Checksum | Footer |
| 2B     | 1B     | 1B   | 2B   | 2B       | Variable          | 2B       | 2B     |
+--------+--------+------+------+----------+-------------------+----------+--------+
```

### ���ݰ�����

| ���� | ���� | ˵�� |
|------|------|------|
| HAND_LANDMARKS | 0x01 | �ֲ��ؼ������� |
| GESTURE_RESULT | 0x02 | ����ʶ���� |
| COMBINED_DATA | 0x03 | ������� |
| HEARTBEAT | 0x04 | ������ |

### HandData �ṹ

```python
@dataclass
class HandData:
    hand_id: str                    # �ֲ�ID
    hand_type: str                  # "Left" �� "Right"
    landmarks: List[List[float]]    # 21���ؼ������� [x, y, z]
    palm_center: Tuple[float, float]  # ��������
    palm_length: float              # ���ƻ�׼����
    timestamp: float                # ʱ���
    confidence: float               # ������Ŷ�
```

### GestureData �ṹ

```python
@dataclass
class GestureData:
    gesture_name: str               # ��������
    hand_type: str                  # "Left" �� "Right"
    confidence: float               # ���Ŷ�
    timestamp: float                # ʱ���
    details: Dict[str, Any]         # ��ϸ��Ϣ
```

## ?? ����˵��

### `config.py` ��������

```python
BLUETOOTH_CONFIG = {
    'enabled': True,                     # ������������
    'server_port': 1,                   # RFCOMM�˿�
    'server_uuid': '94f39d29-7d6d-437d-973b-fba39e49d4ee',
    'device_name': 'HandGestureReceiver',
    'heartbeat_interval': 5.0,          # ����������룩
    'auto_gesture_detection': True      # �Զ����Ƽ��
}
```

## ? ���ߺͲ���

### 1. Э�����

```bash
# ����Э����/���
python -m bluetooth.utils

# ����ʹ�ò��Խű�
python examples/bluetooth_test.py --protocol
```

### 2. �豸����

```bash
# ɨ�������豸
python examples/bluetooth_test.py --discovery

# �������ƽ�����
python -c "from bluetooth.utils import find_gesture_receiver_devices; print(find_gesture_receiver_devices())"
```

### 3. ���ܲ���

```bash
# �������ܻ�׼����
python examples/bluetooth_test.py --performance
```

### 4. ���Ӳ���

```bash
# ������ָ���豸������
python examples/bluetooth_test.py --verify YOUR_BLUETOOTH_ADDRESS
```

## ? ���ܺʹ���

### ���ʹ���ʹ��

| ���� | �ؼ���Ƶ�� | ����Ƶ�� | �ܴ��� |
|------|------------|----------|--------|
| ��Ƶ | 10 FPS | 0.5 FPS | ~2.5 KB/s |
| ��׼ | 30 FPS | 2 FPS | ~7.8 KB/s |
| ��Ƶ | 60 FPS | 5 FPS | ~16.2 KB/s |

### ���ݰ���С

- �ֲ��ؼ����: ~600-800 �ֽ�
- ���ƽ����: ~200-300 �ֽ�
- ������: ~50-80 �ֽ�

## ?? ���ɵ�������Ŀ

### 1. ����PC�˽���

```python
# �� ui/main_window.py ��
from bluetooth.manager import BluetoothManager

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bluetooth_manager = BluetoothManager()
        self.setup_bluetooth()
    
    def setup_bluetooth(self):
        if self.bluetooth_manager.is_bluetooth_enabled():
            self.bluetooth_manager.start_bluetooth_server()
            
            # �����ź�
            self.bluetooth_manager.bluetooth_gesture_detected.connect(
                self.on_bluetooth_gesture
            )
    
    def on_bluetooth_gesture(self, gesture_name, hand_type, confidence):
        print(f"��������: {gesture_name}")
```

### 2. �޸�������������

```python
# �� config.py ���޸�
BLUETOOTH_CONFIG = {
    'enabled': True,  # ��Ϊ True
    # ... ��������
}
```

## ? �����ų�

### ��������

1. **"pybluez��δ��װ"**
   ```bash
   pip install pybluez
   ```

2. **"�޷�������������"**
   - ȷ������������������
   - �����������װ

3. **"����ʧ��"**
   - ȷ���豸��ַ��ȷ
   - ������ǽ����
   - ȷ���豸����Է�Χ��

4. **"���ݴ����ж�"**
   - ��������ź�ǿ��
   - �鿴�������Ƿ�����

### ���Է���

```python
# ������ϸ��־
import logging
logging.basicConfig(level=logging.DEBUG)

# ʹ�ù��ߺ�������
from bluetooth.utils import verify_bluetooth_connection
result = verify_bluetooth_connection("TARGET_ADDRESS")
```

## ? ����ָ��

### ����µ����ݰ�����

1. �� `PacketType` ö�������������
2. ʵ�ֶ�Ӧ�Ĵ��/�������
3. ����Э��汾��

### �Զ������ƴ���

```python
# ������������������Զ��崦��
def custom_gesture_handler(self, gesture_data):
    if gesture_data.gesture_name == "CustomGesture":
        # ִ���Զ��嶯��
        print("ִ���Զ������ƶ���")
```

## ? API �ο�

### BluetoothSender ��Ҫ����

- `connect()`: ���ӵ�PC
- `send_hand_landmarks(hand_data)`: �����ֲ�����
- `send_gesture_result(gesture_data)`: �������ƽ��
- `send_combined_data(hand_data, gesture_data)`: �����������
- `disconnect()`: �Ͽ�����

### BluetoothReceiver ��Ҫ�ź�

- `hand_data_received(HandData)`: ���յ��ֲ�����
- `gesture_detected(GestureData)`: ��⵽����
- `connection_status_changed(bool)`: ����״̬�仯
- `error_occurred(str)`: ��������

### BluetoothManager ��Ҫ����

- `start_bluetooth_server()`: ����������
- `stop_bluetooth_server()`: ֹͣ������
- `is_connected()`: �������״̬
- `enable_bluetooth(enabled)`: ����/��������

## ? ��ȫ����

1. **���ݼ���**: ���������л�����������ݼ���
2. **�豸��֤**: ʵ���豸�����֤����
3. **���ʿ���**: �������ӵ��豸������

## ? �����Ż�����

1. **���ͷ���Ƶ��**: ����Ӧ������������ݷ���Ƶ��
2. **����ѹ��**: �Դ������ݿ���ѹ������
3. **�������**: �������÷��Ͷ��д�С
4. **���Ӹ���**: ����Ƶ������/�Ͽ�����

## ? ����

��ӭ�ύ����͸Ľ����飡��ȷ����

1. ���������Ŀ���
2. ����ʵ��Ĳ���
3. ��������ĵ�
4. �����ڲ�ͬ�����µļ�����

## ? ���֤

����Ŀ��ѭ MIT ���֤����� LICENSE �ļ��� 