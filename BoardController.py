import cv2
from img import Img


class BoardController:
    def __init__(self, board_path, icon_path):
        self.board = Img().read(board_path)
        self.smiley = Img().read(icon_path, size=(50, 50))


        cv2.namedWindow("Main Board",cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Main Board", self.handle_click)

        if not hasattr(cv2, 'WND_PROP_WIDTH'):
            cv2.WND_PROP_WIDTH = 3
        if not hasattr(cv2, 'WND_PROP_HEIGHT'):
            cv2.WND_PROP_HEIGHT = 4

    def handle_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, y)
            h, w = self.board.img.shape[:2]

            cell_w = w / 8
            cell_h = h / 8

            col = int(x // cell_w)
            row = int(y // cell_h)

            smiley_w, smiley_h = 50, 50
            center_x = int((col * cell_w) + (cell_w / 2) - (smiley_w / 2))
            center_y = int((row * cell_h) + (cell_h / 2) - (smiley_h / 2))

            self.smiley.draw_on(self.board, center_x, center_y)
            cv2.imshow("Main Board", self.board.img)

    def run(self):
        while True:
            w = cv2.getWindowProperty("Main Board", cv2.WND_PROP_WIDTH)
            h = cv2.getWindowProperty("Main Board", cv2.WND_PROP_HEIGHT)

            if w > 0 and h > 0 and (self.board.img.shape[1] != int(w) or self.board.img.shape[0] != int(h)):
                self.board.img = cv2.resize(self.board.img, (int(w), int(h)))

            cv2.imshow("Main Board", self.board.img)
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()