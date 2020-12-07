# README

# ETC_CNN<br />Encrypted traffic classification use cnn<br />
采用CNN对加密流量进行分类 当前版本仅支持TCP。<br />第一步：将pcap数据包转换为json。  <br />pcap2json.py <br />-i 后接pcap格式或者pcapng格式文件，也可是包含若干pcap文件的 目录/*。 为了便于后续数据标注，该目录下的pcap应为同一标签类型。<br />-o 输出的目标文件，不设置则默认输出到stdout<br />-s 以双向流提取(默认是单向流）<br />-m 直接将流映射成为xl_map格式（若要使用本工具提供的分类器则为必选。不设置则仅使用本工具提供的组流功能）<br />示例：<br />python3 pcap2json.py  -i  dir/*  -o  out1.json  -s  -m<br />python3 pcap2json.py  -i  test.pcap  -o  out2.json  -s  -m <br />
<br />第二步:将提取的xl_map打上标签<br />label_data.py<br />
<br />-i pcap2json.py （m参数）产生的json文件<br />-o 输出的目标文件，不设置则默认输出到stdout<br />-l 输入json文件中的数据对应的标签<br />注意:将不同标签的数据输出到同一个json文件里方便训练（追加方式写文件），因此最开始需保证输出文件不存在或者内容为空。<br />示例：<br />python3 label_data.py -i out1.json -o out.json -l chat<br />python3 label_data.py -i out2.json -o out.json -l email<br />python3 label_data.py -i out3.json -o out.json -l p2p<br />python3 label_data.py -i out4.json -o out.json -l voip<br />
<br />第三步：读取数据训练<br />python3 etc_cnn.py <br />需要将第二步标注好的json重命名为data.json(这里偷懒未以参数形式读输入文件名）
