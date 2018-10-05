import os
import pandas as pd
from scipy import misc
from torch.utils.data import Dataset
from torchvision import transforms
from torch.utils.data import DataLoader


class XrayDataset(Dataset):

    def __init__(self, datadir, csvpath, transform=None):

        self.datadir = datadir
        self.transform = transform
        self.pathologies = ["Atelectasis", "Consolidation", "Infiltration",
                            "Pneumothorax", "Edema", "Emphysema", "Fibrosis", "Effusion", "Pneumonia",
                            "Pleural_thickening", "Cardiomegaly", "Nodule", "Mass", "Hernia"]

        # Load data
        self.Data = pd.read_csv(csvpath)

    def __len__(self):
        return len(self.Data)

    def __getitem__(self, idx):
        im = misc.imread(os.path.join(self.datadir, self.Data['Image Index'][idx]))

        # Check that images are 2D arrays
        if len(im.shape) > 2:
            im = im[:, :, 0]
        if len(im.shape) < 2:
            print("error, dimension lower than 2 for image", self.Data['Image Index'][idx])

        # Add color channel
        im = im[:, :, None]

        # Tranform
        if self.transform:
            im = self.transform(im)

        return im, self.Data[self.pathologies].loc[idx].values


def MyDataLoader(datadir, csvpath, inputsize, batch_size=16):
    # Transformations
    data_transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(inputsize),
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.repeat(3, 1, 1))
    ])

    # Initialize dataloader
    dataset = XrayDataset(datadir, csvpath, transform=data_transforms)
    dataloader = DataLoader(dataset, shuffle=True, batch_size=batch_size)

    return dataloader


if __name__ == '__main__':

    ####################################################################################################################
    # Test
    ####################################################################################################################

    datadir = "/home/user1/Documents/Data/ChestXray/images"
    csvpath = "/home/user1/Documents/Data/ChestXray/DataTrain.csv"
    inputsize = [224, 224]

    # Transformations
    data_transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize(inputsize),
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x.repeat(3, 1, 1))
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Initialize dataloader
    dataset = XrayDataset(datadir, csvpath, transform=data_transforms)
    dataloader = DataLoader(dataset, shuffle=True, batch_size=16)

    print(len(dataset))

    cpt = 0

    for dataiter in dataloader:
        data, label = dataiter

        cpt += 1
        if cpt > 1:
            break

        print("data", data.size())
        print("label", label.size())
        print("pixel range", data.min(), data.max())
        print("pixel mean", data[:, 0].mean(), data[:, 1].mean(), data[:, 2].mean())
        print("pixel std", data[:, 0].std(), data[:, 1].std(), data[:, 2].std())

        for i in range(3):
            misc.imshow(data[i].numpy())
