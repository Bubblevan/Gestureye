# ���Ƽ��ϵͳ�ܹ�˵��

## ϵͳ�ܹ�����

��ϵͳ����**�ͻ���-������**�ܹ������봫ͳ�ܹ��෴��

- **dyn_gestures**: ����ˣ��������Ƽ������ݷ���
- **project**: �ͻ��ˣ��������ݽ��պͶ���ִ��

## ͨ��ģʽ

### 1. Socketģʽ (TCP/IP)
```
dyn_gestures (�����) --TCP/IP--> project (�ͻ���)
```

**����**:
- `dyn_gestures/config.py`: `CONNECTION_TYPE = 'socket'`
- `project/config.py`: `CONNECTION_TYPE = 'socket'`

### 2. ����ģʽ (RFCOMM)
```
dyn_gestures (�����) --����RFCOMM--> project (�ͻ���)
```

**����**:
- `dyn_gestures/config.py`: `CONNECTION_TYPE = 'serial'`
- `project/config.py`: `CONNECTION_TYPE = 'serial'`

## ��������

### dyn_gestures (�����)
1. **���Ƽ��**: ʹ������ͷ�������
2. **���ݴ���**: ʶ���������ͺ����Ŷ�
3. **���ݷ���**: ͨ��socket���͵�project
   - Socketģʽ: ʹ��TCP/IP���͵�ָ��IP�Ͷ˿�
   - ����ģʽ: ʹ��RFCOMM���͵�ָ��MAC��ַ�Ͷ˿�

### project (�ͻ���)
1. **���ݽ���**: ͨ��socket��������dyn_gestures������
   - Socketģʽ: ����TCP/IP�˿�
   - ����ģʽ: ����RFCOMM�˿�
2. **���ݴ���**: ������������
3. **����ִ��**: �������ư�ִ����Ӧ����

## ����һ����Ҫ��

### ��Ҫ��������Ŀ�����ñ���һ�£�

| ��Ŀ | CONNECTION_TYPE | ˵�� |
|------|----------------|------|
| dyn_gestures | `'socket'` | ʹ��TCP/IP�������� |
| project | `'socket'` | ʹ��TCP/IP�������� |
| dyn_gestures | `'serial'` | ʹ������RFCOMM�������� |
| project | `'serial'` | ʹ������RFCOMM�������� |

### ��������
��ʹ������ģʽʱ������Ҫ���ã�

**dyn_gestures/config.py**:
```python
CONNECTION_TYPE = 'serial'
BLUETOOTH_MAC = 'project������MAC��ַ'  # projectӦ�õ�����MAC��ַ
BLUETOOTH_PORT = 4
```

**project/config.py**:
```python
CONNECTION_TYPE = 'serial'
BLUETOOTH_MAC = 'XX:XX:XX:XX:XX:XX'  # �Զ������ֶ�����
BLUETOOTH_PORT = 4
```

## ��������

### 1. Ϊʲô�л�ͨ�ŷ�ʽ��Ҫ������Σ�
**ԭ��**: ���ò�һ�µ��¿ͻ��˳�ʼ��ʧ��
**���**: ȷ��������Ŀ��`CONNECTION_TYPE`����һ��

### 2. Ϊʲô��ʾ"socket������������"������������������
**ԭ��**: ������������ʼ��ʧ�ܣ��Զ�������socketģʽ
**���**: 
- ����Ƿ�װ��`pybluez`
- ������������Ƿ�����
- ���MAC��ַ�����Ƿ���ȷ

### 3. Ϊʲô�޷����յ��������ݣ�
**����嵥**:
- [ ] ������Ŀ��`CONNECTION_TYPE`һ��
- [ ] ����ģʽ��MAC��ַ������ȷ
- [ ] ����/������������
- [ ] ����ǽδ��ֹ����

## ���Է���

### 1. �������
```bash
# ���dyn_gestures����
cat dyn_gestures/config.py | grep CONNECTION_TYPE

# ���project����  
cat project/config.py | grep CONNECTION_TYPE
```

### 2. ��������
```bash
# ����Socket����
cd project
python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 65432)); print('Socket���ӳɹ�')"

# ������������
cd project
python get_linux_bluetooth_mac.py
```

### 3. �鿴��־
- dyn_gestures: �鿴����̨�����������Ϣ
- project: �鿴UI��־���ķ�����״̬

## �л�ͨ�ŷ�ʽ����

### ��Socket�л�������
1. **ֹͣ����Ӧ��**
2. **�޸�dyn_gestures����**:
   ```python
   CONNECTION_TYPE = 'serial'
   BLUETOOTH_MAC = 'project������MAC��ַ'
   ```
3. **�޸�project����**:
   ```python
   CONNECTION_TYPE = 'serial'
   ```
4. **����projectӦ��**����UI���л�������ģʽ
5. **����dyn_gesturesӦ��**

### �������л���Socket
1. **ֹͣ����Ӧ��**
2. **�޸�dyn_gestures����**:
   ```python
   CONNECTION_TYPE = 'socket'
   SOCKET_HOST = 'project��IP��ַ'
   ```
3. **�޸�project����**:
   ```python
   CONNECTION_TYPE = 'socket'
   ```
4. **��������Ӧ��**

## ����ϸ��

### Socketͨ��
- **Э��**: TCP/IP
- **�˿�**: 65432 (Ĭ��)
- **���ݸ�ʽ**: JSON
- **����**: UTF-8

### ����ͨ��
- **Э��**: RFCOMM
- **�˿�**: 4 (Ĭ��)
- **���ݸ�ʽ**: JSON
- **����**: UTF-8

### ���ݸ�ʽʾ��
```json
{
    "type": "gesture_detection",
    "gesture": "HandOpen",
    "hand_type": "Right",
    "confidence": 95.5,
    "gesture_type": "dynamic",
    "timestamp": 1234567890.123,
    "details": {
        "tag": "end"
    }
}
``` 