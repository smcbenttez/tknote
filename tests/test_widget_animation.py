import unittest

from widget_animation import WidgetAnimation, AnimationFrame


class TestWidgetAnimation(unittest.TestCase):

    def setUp(self):
        # self.animation = WidgetAnimation(
        #     widget=None,
        #     parent_widget=None,
        #     begin_x=0,
        #     begin_y=600,
        #     final_x=0,
        #     final_y=0,
        #     target_fps=60,
        #     duration=1000
        # )
        # self.animation = WidgetAnimation(
        #     widget=None,
        #     parent_widget=None,
        #     begin_x=0,
        #     begin_y=0,
        #     final_x=100,
        #     final_y=100,
        #     target_fps=60,
        #     duration=1000
        # )
        # self.begin_x = 0
        # self.begin_y = 0
        # self.final_x = 100
        # self.final_y = 100
        # self.target_fps = 20
        # self.duration = 5000
        # self.total_frames = self.duration / 1000 * self.target_fps
        # self.begin_x = 0
        # self.begin_y = 0
        # self.final_x = 100
        # self.final_y = 100
        # self.target_fps = 20
        # self.duration = 500
        # self.total_frames = self.duration / 1000 * self.target_fps
        self.begin_x = 0
        self.begin_y = 600
        self.final_x = 0
        self.final_y = 0
        self.target_fps = 20
        self.duration = 5000
        self.total_frames = self.duration / 1000 * self.target_fps
        self.animation = WidgetAnimation(
            widget=None,
            parent_widget=None,
            begin_x=self.begin_x,
            begin_y=self.begin_y,
            final_x=self.final_x,
            final_y=self.final_y,
            target_fps=self.target_fps,
            duration=self.duration
        )
        # self.animation = WidgetAnimation(
        #     widget=None,
        #     parent_widget=None,
        #     begin_x=0,
        #     begin_y=0,
        #     final_x=100,
        #     final_y=100,
        #     target_fps=60,
        #     duration=5000
        # )
        # self.animation = WidgetAnimation(
        #     widget=None,
        #     parent_widget=None,
        #     begin_x=37,
        #     begin_y=374,
        #     final_x=-344,
        #     final_y=345,
        #     target_fps=60,
        #     duration=1000
        # )

    def test_frame_time_in_msec(self):
        self.assertEqual(
            self.animation._frame_time_in_msec,
            1000 / self.target_fps
        )

    def test_elapsed_time(self):
        frame_data = list(self.animation)
        self.assertEqual(
            round(frame_data[-1].elapsed),
            self.duration
        )

    def test_final_frame(self):
        frame_data = list(self.animation)
        self.assertTrue(
            frame_data[-1].final_frame
        )

    def test_total_frames(self):
        frame_data = list(self.animation)
        self.assertEqual(
            frame_data[-1].frame_number,
            (self.duration / 1000) * self.target_fps
        )

    def test_final_pos(self):
        frame_data = list(self.animation)
        self.assertEqual(
            frame_data[-1].x,
            self.final_x
        )
        self.assertEqual(
            frame_data[-1].y,
            self.final_y
        )
