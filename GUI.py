import tkinter as tk
from tkinter import filedialog, messagebox
from Data.PDF_to_XML import process_pdf_to_xml

class PDFToXMLConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to XML Converter")

        # Set the icon
        self.root.iconbitmap("Files/icon/6836874.ico")

        # PDF and XML directories
        self.pdf_directory = tk.StringVar()
        self.xml_directory = tk.StringVar()

        # GUI elements
        self.create_widgets()

    def create_widgets(self):
        # PDF Directory
        pdf_label = tk.Label(self.root, text="PDF Directory:")
        pdf_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        pdf_entry = tk.Entry(self.root, textvariable=self.pdf_directory, width=40)
        pdf_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        pdf_browse_button = tk.Button(self.root, text="Browse", command=self.browse_pdf_directory)
        pdf_browse_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)

        # XML Directory
        xml_label = tk.Label(self.root, text="XML Directory:")
        xml_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        xml_entry = tk.Entry(self.root, textvariable=self.xml_directory, width=40)
        xml_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        xml_browse_button = tk.Button(self.root, text="Browse", command=self.browse_xml_directory)
        xml_browse_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.W)

        # Convert Button
        convert_button = tk.Button(self.root, text="Convert PDF to XML", command=self.convert_pdf_to_xml)
        convert_button.grid(row=2, column=0, columnspan=3, pady=20)

    def browse_pdf_directory(self):
        pdf_directory = filedialog.askdirectory()
        self.pdf_directory.set(pdf_directory)

    def browse_xml_directory(self):
        xml_directory = filedialog.askdirectory()
        self.xml_directory.set(xml_directory)

    def convert_pdf_to_xml(self):
        pdf_directory = self.pdf_directory.get()
        xml_directory = self.xml_directory.get()

        try:
            # Call the conversion function directly
            process_pdf_to_xml(pdf_directory, xml_directory)
            messagebox.showinfo("XML Generated", "XML files have been generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToXMLConverterApp(root)
    root.mainloop()
