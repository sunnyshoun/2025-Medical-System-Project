# data sheet at 04/17/25 1525

thickness = [
    10,
    10,
    10,
    10,
    5,
    5,
    5,
    5,
    5,
    4,
    4,
    4,
    3,
    3,
    3
]

distance = [
    0.7932037352,
    1.586410826,
    2.379617172,
    3.17282333,
    1.983014707,
    2.379617731,
    2.776220744,
    3.17282375,
    3.569426752,
    3.1728238,
    3.490106197,
    3.807388593,
    3.093503241,
    3.331465036,
    3.569426831
]

def get_thick_dis(degree: float):
    k = int((degree-0.1)*10)
    if k < 0 or k > 14:
        raise ValueError(f"Invalid degree: {degree}")
    return {"thickness":thickness[k], "distance":distance[k]}

if __name__ == "__main__":
    print(get_thick_dis(0.1))
    print(get_thick_dis(1.5))
