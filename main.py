from customtkinter import * 
from tkinter import filedialog

def main():

    def click_handler():
        file_path = filedialog.askopenfilename(
            title = "Select an image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
        )
        if file_path:
            print("Hi")

    main = CTk()
    w_height = 600
    w_width = 900
    main.geometry(f"{w_width}x{w_height}")
    main.title("Object detection in adverse weather")
    
    title = CTkLabel(main, text="Object detection in adverse weather", font=('Arial', 28))
    title.place(relx=0.5, rely=0.25, anchor="center")
    description = CTkLabel(main, text="Upload an image to detect the object", font=('Arial', 18))
    description.place(relx=0.5, rely=0.30, anchor="center")
    load_img_button = CTkButton(main, text="hi >_< hewoooo", corner_radius=32, font=('arial', 18), command=click_handler)
    load_img_button.place(relx=0.5, rely=0.5, anchor="center")

    main.mainloop()



if __name__ == "__main__":
    main()

