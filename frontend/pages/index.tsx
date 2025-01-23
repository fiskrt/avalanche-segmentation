import { BACKEND_URI } from '@/config';
import { useRouter } from 'next/router';
import { useRef, useState } from "react";

interface UploadedPage {
  id: number;
  description: string;
  image: string;
}

interface ProcessedImage {
  description: string;
  image: string;
}

interface ClickCoordinates {
  x: number;
  y: number;
}

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [processedImages, setProcessedImages] = useState<ProcessedImage[]>([]);
  const [isGenerated, setIsGenerated] = useState(false);
  const [generatedPages, setGeneratedPages] = useState<UploadedPage[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [additionalPrompt, setAdditionalPrompt] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isOpenType, setIsOpenType] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [clickCoordinates, setClickCoordinates] = useState<ClickCoordinates | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [isSpam, setIsSpam] = useState(false);
  const [isImageApproved, setIsImageApproved] = useState<boolean | null>(null);
  const [isSpamCheckComplete, setIsSpamCheckComplete] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [avalancheType, setAvalancheType] = useState<string | null>(null);


  // Add these handler functions before the return statement
  const handleImageApprove = () => {
    setIsImageApproved(true);
    setClickCoordinates(null); // Reset any existing click coordinates
  };

  const handleImageReject = () => {
    setIsImageApproved(false);
  };

  // Add this function before handleFileChange
  const checkIfSpam = async (file: File): Promise<boolean> => {

    // send the coordinates to the backend
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BACKEND_URI}/spamcheck/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload files');
    }
    const data = await response.json();
    console.log(data);
    return data.spam
  };

  const predictAvalancheType = async (file: File) => {
    // send the coordinates to the backend
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BACKEND_URI}/checkavalanchetype/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload files');
    }
    const data = await response.json();
    console.log(data);

    // map avalanche_type (0,1,2,3) to the avalancheType array
    const avalancheType = possibleavalancheTypes[data.avalanche_type];
    console.log(avalancheType);
    return avalancheType;

  }
  const possibleavalancheTypes = [
    "none",
    'slab',
    'loose',
    'glide'
  ];

  const options = [
    "Small",
    "Medium",
    "Large",
    "Very Large"
  ];

  const handleImageClick = async (event: React.MouseEvent<HTMLImageElement>) => {
    if (!imageRef.current) return;

    // Get image element's bounding rectangle
    const rect = imageRef.current.getBoundingClientRect();
    const image = imageRef.current;

    // Get the scaling factor between natural and displayed image sizes
    const scaleX = image.naturalWidth / rect.width;
    const scaleY = image.naturalHeight / rect.height;

    // Calculate coordinates relative to the original image size
    const x = Math.round((event.clientX - rect.left) * scaleX);
    const y = Math.round((event.clientY - rect.top) * scaleY);

    setClickCoordinates({ x, y });
    console.log(`Clicked at: ${x}, ${y} on original image`);


    // send the coordinates to the backend
    const formData = new FormData();
    if (uploadedImage) {
      formData.append('file', uploadedImage);
    }

    // pass only the x,y coordinates (as int!!)
    const response = await fetch(`${BACKEND_URI}/add_point/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', // Indicate the payload is JSON
      },
      body: JSON.stringify({
        x: x, // Ensure x is an integer
        y: y  // Ensure y is an integer
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to upload files');
    }
    const data = await response.json();
    console.log(data);

    // Assuming `data.image` is the Base64 encoded image string
    if (data.image) {
      const base64Image = `data:image/png;base64,${data.image}`;
      setPreviewUrl(base64Image); // Update the preview image URL
    } else {
      throw new Error('Invalid image data received');
    }
    // here i get the image
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setUploadedImage(files[0]);

    setIsLoading(true);
    setClickCoordinates(null); // Reset coordinates when new image is uploaded
    setIsSpam(false);
    setIsImageApproved(null);
    setIsSpamCheckComplete(false);


    // Create preview URL
    const file = files[0];
    const preview = URL.createObjectURL(file);
    setPreviewUrl(preview);
    const spamCheckResult = await checkIfSpam(file);
    setIsSpamCheckComplete(true);
    setIsLoading(false);

    if (spamCheckResult) {
      setIsSpam(true);
      setIsLoading(false);
      setProcessedImages([]);
      setGeneratedPages([]);
      return;
    }

    // Send the image to the backend to predict avalanche type
    const possibleAvalancheType = await predictAvalancheType(file);
    if (possibleAvalancheType) {
      setAvalancheType(possibleAvalancheType);
    }


    try {
      // Simulate API response to check spam image
      await new Promise(resolve => setTimeout(resolve, 3000));

      const fakeData = [{
        description: "",
        image: preview
      }];

      console.log("hi");

      //if image is spam, return is spam


      setProcessedImages(fakeData);

      const pages = fakeData.map((item: ProcessedImage, index: number) => ({
        id: index + 1,
        description: item.description,
        image: item.image,
      }));

      setGeneratedPages(pages);
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Failed to upload files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoToEditor = async () => {
    if (!isGenerated || generatedPages.length === 0) return;

    try {
      router.push({
        pathname: '/editor',
        query: {
          pages: JSON.stringify(generatedPages),
        }
      });
    } catch (error) {
      console.error('Error navigating to editor:', error);
      alert('Failed to navigate to editor. Please try again.');
    }
  };

  return (
    <div className="bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="min-h-screen pt-10">
        <div className="container mx-auto px-4 max-w-3xl text-center space-y-20">
          <img
            src="/logoslf.png"
            alt="Dilo"
            className="mx-auto w-32 object-contain"
          />

          <div className="bg-white p-8 rounded-2xl shadow-lg space-y-6">
            <h4 className="text-2xl font-bold text-gray-800">
              {previewUrl ? "Uploaded Image" : "Upload your image here 📄"}
            </h4>
            {previewUrl && (
              <p className='text-xl font-bold text-gray-800'>Preview</p>
            )}

            <div className="space-y-8">
              {(!previewUrl || isSpam) && (
                <div className="flex justify-center">
                  <label className="flex flex-col items-center px-4 py-6 bg-white text-blue-600 rounded-lg shadow-lg border-2 border-blue-100 border-dashed hover:bg-blue-50 transition-colors cursor-pointer">
                    <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span className="mt-2 text-base">Choose files</span>
                    <input
                      type="file"
                      className="hidden"
                      onChange={handleFileChange}
                      accept="image/*"
                    />
                  </label>
                </div>
              )}
              {isSpam && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">
                        This image has been flagged as inappropriate content. Please upload a different image.
                      </p>
                    </div>
                  </div>
                </div>
              )}


              {previewUrl && !isSpam && isSpamCheckComplete && (
                <div className="max-w-xl mx-auto space-y-4">
                  <div className="relative">
                    <img
                      ref={imageRef}
                      src={previewUrl}
                      alt="Preview"
                      className="max-w-full h-auto rounded-lg shadow-md cursor-crosshair"
                      onClick={isImageApproved === false ? handleImageClick : undefined}
                    />
                    {clickCoordinates && isImageApproved === false && (
                      <p>
                        Clicked at: {clickCoordinates.x}px, {clickCoordinates.y}px </p>
                    )}
                  </div>

                  {isImageApproved === null && (
                    <div className="flex justify-center gap-4">
                      <button
                        onClick={handleImageApprove}
                        className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                        </svg>
                        Accept Image
                      </button>
                      <button
                        onClick={handleImageReject}
                        className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Reject Image
                      </button>
                    </div>
                  )}

                  {isImageApproved === false && (
                    <p className="text-sm text-gray-600">Click on the image to mark the problematic area</p>
                  )}
                </div>
              )}

              {previewUrl && !isSpam && isImageApproved === true && (
                <div className="max-w-xl mx-auto space-y-4">
                  <div className="relative">
                    <textarea
                      value={additionalPrompt}
                      onChange={(e) => {
                        const text = e.target.value;
                        if (text.length <= 500) {
                          setAdditionalPrompt(text);
                        }
                      }}
                      placeholder="Add a description"
                      className="w-full px-4 py-3 text-gray-800 rounded-xl border-2 border-blue-100 
                    focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500
                    placeholder:text-gray-400
                    transition-all duration-200
                    min-h-[100px] resize-none
                    bg-white"
                    />
                    <div className="absolute bottom-2 right-2 text-sm text-gray-400">
                      {additionalPrompt.length}/500
                    </div>
                  </div>

                  <div className="relative text-center flex justify-center items-center">
                    <p className="mb-0 mr-2 text-gray-700 font-bold">
                      Our model predicted Avalanche type as
                    </p>
                    <span className="text-blue-400">{avalancheType}</span>
                  </div>

                  <div className="relative text-center flex justify-center items-center">

                    <button
                      onClick={() => setIsOpenType(!isOpenType)}
                      className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      {selectedType || "Select Avalanche Type"}
                      <svg
                        className="-mr-1 ml-2 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        aria-hidden="true"
                      >
                        <path
                          fillRule="evenodd"
                          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>
                    {isOpenType && (
                      <div
                        className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
                        role="menu"
                      >
                        <div className="py-1" role="none">
                          {possibleavalancheTypes.map((option, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                setSelectedType(option);
                                setIsOpenType(false);
                              }}
                              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                            >
                              {option}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>


                  <div className="relative text-center flex justify-center items-center">

                    <button
                      onClick={() => setIsOpen(!isOpen)}
                      className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      {selected || "Select Avalanche Size"}
                      <svg
                        className="-mr-1 ml-2 h-5 w-5"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                        aria-hidden="true"
                      >
                        <path
                          fillRule="evenodd"
                          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>

                    {isOpen && (
                      <div
                        className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
                        role="menu"
                      >
                        <div className="py-1" role="none">
                          {options.map((option, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                setSelected(option);
                                setIsOpen(false);
                              }}
                              className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                            >
                              {option}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="py-4">
              <p className={`text-lg font-medium ${isGenerated ? 'text-green-600' : 'text-gray-600'}`}>
                {!isLoading && !isGenerated && "Please upload a file to continue"}
                {isLoading && "Processing..."}
                {isGenerated && "Generation complete! 🚀"}
              </p>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={handleGoToEditor}
                disabled={!isGenerated || isLoading}
                className={`
                  px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200
                  flex items-center gap-2
                  ${!isGenerated || isLoading
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed opacity-75 shadow-none'
                    : 'bg-gradient-to-r from-violet-600 to-blue-500 text-white shadow-lg hover:opacity-90 hover:shadow-violet-200/50 shadow-violet-200/30'
                  }
                `}
              >
                <span>📝</span>
                Go to Editor
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}