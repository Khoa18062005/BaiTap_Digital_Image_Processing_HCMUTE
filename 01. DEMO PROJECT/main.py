from core.image_processor import ImageProcessor
from presenters.gallery_presenter import GalleryPresenter
from presenters.frequency_presenter import FrequencyPresenter

from ui.selection_view import SelectionView
from ui.main_view import MainView
from ui.main_view_f import MainViewF


class AppController:
    def __init__(self):
        # Trạng thái mặc định ban đầu là mở Menu Chọn
        self.state = "MENU"

    def run(self):
        # Vòng lặp này giúp chương trình không bị chết khi đóng 1 cửa sổ
        while self.state != "EXIT":

            if self.state == "MENU":
                app = SelectionView(
                    on_spatial_selected=self.go_spatial,
                    on_frequency_selected=self.go_frequency
                )
                app.mainloop()  # Chặn ở đây cho đến khi cửa sổ đóng
                # Nếu cửa sổ đóng mà không chọn gì (Bấm dấu X), thoát hoàn toàn
                if self.state == "MENU":
                    self.state = "EXIT"

            elif self.state == "SPATIAL":
                view = MainView()
                processor = ImageProcessor()
                presenter = GalleryPresenter(view, processor)
                view.set_presenter(presenter)

                # Cài đặt lệnh khi bấm "Quay về"
                view.set_back_callback(self.go_menu)
                view.run()

                if self.state == "SPATIAL":
                    self.state = "EXIT"

            elif self.state == "FREQUENCY":
                view = MainViewF()
                processor = ImageProcessor()
                presenter = FrequencyPresenter(view, processor)
                view.set_presenter(presenter)

                # Cài đặt lệnh khi bấm "Quay về"
                view.set_back_callback(self.go_menu)
                view.run()

                if self.state == "FREQUENCY":
                    self.state = "EXIT"

    # Các hàm chuyển đổi trạng thái
    def go_spatial(self):
        self.state = "SPATIAL"

    def go_frequency(self):
        self.state = "FREQUENCY"

    def go_menu(self):
        self.state = "MENU"

if __name__ == "__main__":
    controller = AppController()
    controller.run()