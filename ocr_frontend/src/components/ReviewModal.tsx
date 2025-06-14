import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageId: string;
  imageUrl: string;
  initialJson: string;
  onSave: () => void;
}

const ReviewModal: React.FC<ReviewModalProps> = ({
  isOpen,
  onClose,
  imageId,
  imageUrl,
  initialJson,
  onSave,
}) => {
  const [jsonString, setJsonString] = useState(initialJson);
  const [jsonError, setJsonError] = useState<string | null>(null);
  const { fetchWithAuth } = useAuth();

  if (!isOpen) return null;

  const handleSave = async () => {
    try {
      // Validate JSON before saving
      JSON.parse(jsonString);
      
      const response = await fetchWithAuth('/update-image-json', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_id: imageId,
          json_data: jsonString,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update JSON data');
      }

      toast.success('JSON data saved successfully!', {
        duration: 3000,
        position: 'top-right',
        style: {
          background: '#10B981',
          color: '#fff',
          padding: '16px',
          borderRadius: '8px',
        },
      });

      onSave();
      onClose();
    } catch (error) {
      console.error('Error saving JSON data:', error);
      toast.error('Failed to save changes. Please try again.', {
        duration: 4000,
        position: 'top-right',
        style: {
          background: '#EF4444',
          color: '#fff',
          padding: '16px',
          borderRadius: '8px',
        },
      });
    }
  };

  const handleDiscard = () => {
    setJsonString(initialJson);
    setJsonError(null);
    onClose();
  };

  const handleJsonChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setJsonString(value);
    // Only show error if the JSON is completely invalid
    try {
      JSON.parse(value);
      setJsonError(null);
    } catch (error) {
      // Don't set error while typing, only if the JSON is completely invalid
      if (value.trim() === '') {
        setJsonError(null);
      } else {
        setJsonError('Invalid JSON format');
      }
    }
  };

  const formatJson = (jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 4);
    } catch (error) {
      return jsonString;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[90vw] h-[90vh] flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-xl font-semibold">Review Image Results</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        <div className="flex-1 flex overflow-hidden">
          {/* Left side - Image */}
          <div className="w-1/2 p-4 border-r overflow-auto">
            <img
              src={imageUrl}
              alt="Processed image"
              className="max-w-full h-auto"
            />
          </div>

          {/* Right side - JSON Editor */}
          <div className="w-1/2 p-4 flex flex-col">
            <div className="flex-1 overflow-auto">
              <div className="h-full flex flex-col">
                <textarea
                  value={formatJson(jsonString)}
                  onChange={handleJsonChange}
                  className="flex-1 w-full p-4 font-mono text-sm border rounded bg-gray-50"
                  spellCheck={false}
                  style={{
                    tabSize: 4,
                    whiteSpace: 'pre',
                    wordWrap: 'normal',
                    overflowX: 'auto'
                  }}
                />
                {jsonError && (
                  <div className="text-red-500 text-sm mt-2">
                    {jsonError}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 flex justify-end space-x-2">
              <button
                onClick={handleSave}
                disabled={!!jsonError}
                className={`px-4 py-2 rounded ${
                  jsonError 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-green-600 hover:bg-green-700'
                } text-white`}
              >
                Apply
              </button>
              <button
                onClick={handleDiscard}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewModal;