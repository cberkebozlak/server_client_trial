import React, { useState } from "react";
import { ChevronRight, Folder, FileJson, ChevronDown } from "lucide-react";

const DirectoryUI = () => {
  const [selectedPath, setSelectedPath] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedDirs, setExpandedDirs] = useState(["components"]);
  const [method, setMethod] = useState("GET");
  const [requestBody, setRequestBody] = useState("");

  // Updated directory structure with RESTful API query parameters
  const directory = {
    components: {
      type: "directory",
      path: "components",
      children: {
        door: {
          type: "directory",
          path: "components?component_id=door",
        },
        engine: {
          type: "directory",
          path: "components?component_id=engine",
          children: {
            faults: {
              type: "endpoint",
              path: "faults?component_id=engine",
            },
            operation_update: {
              type: "endpoint",
              path: "operations?component_id=engine",
            },
          },
        },
      },
    },
  };

const toggleDirectory = (path, e) => {
  e.stopPropagation();
  setExpandedDirs((prev) =>
    prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
  );
};

const handleSelect = (path) => {
  setSelectedPath(path);
  // Reset request body when selecting a new endpoint
  setRequestBody("");
};

const fetchData = async () => {
  if (!selectedPath) {
    setResponse({ message: "Please select an endpoint or folder" });
    return;
  }

  setLoading(true);
  try {
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (method === "PUT" && requestBody) {
      options.body = requestBody;
    }

    const API_BASE_URL = "https://server-client-trial.onrender.com";
    const response = await fetch(`${API_BASE_URL}/${selectedPath}`, options);    
    const data = await response.json();
    setResponse(data);
  } catch (error) {
    setResponse({ error: "Failed to fetch data" });
  }
  setLoading(false);
};

const renderDirectory = (structure, path = "", level = 0) => {
  return Object.entries(structure).map(([key, value]) => {
    const currentPath = path ? `${path}/${key}`.replace(/\/+/g, "/") : key;
    const padding = `pl-${level * 4 + 4}`;

    if (value.type === "directory") {
      const isExpanded = expandedDirs.includes(currentPath);

      return (
        <div key={currentPath}>
          <div
            className={`flex items-center p-2 hover:bg-gray-100 cursor-pointer ${padding} ${
              selectedPath === value.path ? "bg-gray-100" : ""
            } ${value.path === "components" ? "" : "ml-4"}`}
            onClick={() => handleSelect(value.path)}
          >
            <div onClick={(e) => toggleDirectory(currentPath, e)} className={`flex items-center mr-2`}>
              {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
            <Folder className="w-4 h-4 mr-2" />
            <span className="text-sm">{key}</span>
          </div>

          {isExpanded && value.children && <div>{renderDirectory(value.children, currentPath, level + 1)}</div>}
        </div>
      );
    } else {
      return (
        <div
          key={currentPath}
          className={`flex items-center p-2 hover:bg-gray-100 cursor-pointer ${padding} ${
            selectedPath === value.path ? "bg-gray-100" : ""
          } ${value.path === "components" ? "" : "ml-6"}`}
          onClick={() => handleSelect(value.path)}
        >
          <div className="w-4 h-4 mr-2" />
          <FileJson className="w-4 h-4 mr-2" />
          <span className="text-sm">{key}</span>
        </div>
      );
    }
  });
};

return (
  <div className="flex h-screen bg-gray-100">
    {/* Left Sidebar */}
    <div className="w-64 bg-white border-r overflow-auto">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-4">Directory</h2>
        {renderDirectory(directory)}
      </div>
    </div>

    {/* Main Content */}
    <div className="flex-1 p-6 overflow-auto">
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b p-4">
          <h2 className="text-xl font-semibold">Request</h2>
        </div>
        <div className="p-4">
          <div className="flex items-center space-x-4 mb-6">
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="bg-blue-100 text-blue-800 px-3 py-1 rounded cursor-pointer"
            >
              <option value="GET">GET</option>
              <option value="PUT">PUT</option>
            </select>
            <div className="flex-1 bg-gray-100 p-2 rounded">
              {selectedPath ? `http://127.0.0.1:8000/${selectedPath}` : "Select a folder or endpoint from the directory"}
            </div>
            <button
              onClick={fetchData}
              disabled={loading || !selectedPath}
              className={`flex items-center px-4 py-2 rounded ${
                loading || !selectedPath ? "bg-gray-300 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600 text-white"
              }`}
            >
              {loading ? "Loading..." : <>Send <ChevronRight className="ml-2 w-4 h-4" /></>}
            </button>
          </div>

          {/* Request Body Section */}
          {method === "PUT" && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Request Body</h3>
              <textarea
                value={requestBody}
                onChange={(e) => setRequestBody(e.target.value)}
                placeholder='{"operationId": "ACC_Controller", "enabled_status": false}'
                className="w-full h-32 p-2 border rounded font-mono text-sm"
              />
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold mb-2">Response</h3>
            <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-auto max-h-96">
              <pre className="whitespace-pre-wrap">
                {response ? JSON.stringify(response, null, 2) : "No response yet"}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);
};

export default DirectoryUI;
