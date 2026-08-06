from networksecurity.utils.main_utils.utils import load_object

model = load_object("final_model/model.pkl")

print(type(model))