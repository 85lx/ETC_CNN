��һ������pcap���ݰ�ת��Ϊjson��  
pcap2json.py 
-i ���pcap��ʽ����pcapng��ʽ�ļ���Ҳ���ǰ�������pcap�ļ��� Ŀ¼/*�� Ϊ�˱��ں������ݱ�ע����Ŀ¼�µ�pcapӦΪͬһ��ǩ���͡�
-o �����Ŀ���ļ�����������Ĭ�������stdout
-s ��˫������ȡ(Ĭ���ǵ�������
-m ֱ�ӽ���ӳ���Ϊxl_map��ʽ����Ҫʹ�ñ������ṩ�ķ�������Ϊ��ѡ�����������ʹ�ñ������ṩ���������ܣ�
ʾ����
python3 pcap2json.py  -i  dir/*  -o  out1.json  -s  -m
python3 pcap2json.py  -i  test.pcap  -o  out2.json  -s  -m 

�ڶ���:����ȡ��xl_map���ϱ�ǩ
label_data.py

-i pcap2json.py ��m������������json�ļ�
-o �����Ŀ���ļ�����������Ĭ�������stdout
-l ����json�ļ��е����ݶ�Ӧ�ı�ǩ
ע��:����ͬ��ǩ�����������ͬһ��json�ļ��﷽��ѵ����׷�ӷ�ʽд�ļ���������ʼ�豣֤����ļ������ڻ�������Ϊ�ա�
ʾ����
python3 label_data.py -i out1.json -o out.json -l chat
python3 label_data.py -i out2.json -o out.json -l email
python3 label_data.py -i out3.json -o out.json -l p2p
python3 label_data.py -i out4.json -o out.json -l voip

����������ȡ����ѵ��
python3 etc_cnn.py 
��Ҫ���ڶ�����ע�õ�json������Ϊdata.json(����͵��δ�Բ�����ʽ�������ļ�����

