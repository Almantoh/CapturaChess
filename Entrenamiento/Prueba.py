from ultralytics import YOLO

if __name__ == '__main__':

    # Aqui tienes varios modelos. https://docs.ultralytics.com/tasks/classify/#models
    # yolov8n-cls.pt -> nano
    # yolov8s-cls.pt -> small
    # yolov8m-cls.pt -> medium
    model = YOLO('yolov8s-cls.pt')  # load a pretrained model (recommended for training)

    # Training.
    results = model.train(
        data='./Datasets/2Gloriosa',
        epochs=300,  # 100 - Numero de iteraciones
        imgsz=640,  # 640 - Es el default
        name='2_fichasAjedrez_small',
        project='./Resultados',
        plots=True,  # Informacion visual
        patience=50,
        batch=-1
    )
