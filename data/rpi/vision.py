# data sheet at 04/19/25 1410

# 螢幕參數	
# 螢幕對角線(inch)	    1.3
# 螢幕寬度(m)	        0.02953398585
# 螢幕寬像素數(pixel)	128

# 結果	
# 最大距離(m)	    2.379617888
# 最小間距(m)	    0.1586411966
# 最大間距(m)	    0.2379619036
# 最小圖像(pixel)	2

thickness = [
    4,
    3,
    3,
    3,
    3,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2
]

distance = [
    0.3172814941,
    0.4759232479,
    0.7138851515,
    0.9518469991,
    1.189808824,
    0.9518470924,
    1.110488298,
    1.2691295,
    1.427770701,
    1.5864119,
    1.745053099,
    1.903694297,
    2.062335494,
    2.220976691,
    2.379617888
]

def get_thick_dis(degree: float):
    k = int((degree-0.1)*10)
    if k < 0 or k > 14:
        raise ValueError(f"Invalid degree: {degree}")
    return {"thickness":thickness[k], "distance":distance[k]}

if __name__ == "__main__":
    print(get_thick_dis(0.1))
    print(get_thick_dis(1.5))
