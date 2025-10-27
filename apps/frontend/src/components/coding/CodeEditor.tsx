import React, { useRef, useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import { LanguageType } from '../../types/coding';
import { CodingService } from '../../services/coding';
import { 
  PlayIcon, 
  DocumentDuplicateIcon, 
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  SunIcon,
  MoonIcon,
  CogIcon
} from '@heroicons/react/24/outline';

interface CodeEditorProps {
  language: LanguageType;
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  height?: string;
  theme?: 'light' | 'dark';
  onRun?: () => void;
  isRunning?: boolean;
  showToolbar?: boolean;
}

const CodeEditor = ({
  language,
  value,
  onChange,
  readOnly = false,
  height = '400px',
  theme = 'light',
  onRun,
  isRunning = false,
  showToolbar = true
}) => {
  const editorRef = useRef<any>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTheme, setCurrentTheme] = useState(theme);
  const [fontSize, setFontSize] = useState(14);
  const [showSettings, setShowSettings] = useState(false);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Configure editor options
    editor.updateOptions({
      fontSize,
      minimap: { enabled: true, scale: 1 },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: language === 'python' ? 4 : 2,
      insertSpaces: true,
      wordWrap: 'on',
      lineNumbers: 'on',
      glyphMargin: true,
      folding: true,
      lineDecorationsWidth: 10,
      lineNumbersMinChars: 3,
      renderLineHighlight: 'line',
      selectOnLineNumbers: true,
      roundedSelection: false,
      readOnly,
      cursorStyle: 'line',
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      },
      suggest: {
        showKeywords: true,
        showSnippets: true,
        showFunctions: true,
        showConstructors: true,
        showFields: true,
        showVariables: true,
        showClasses: true,
        showStructs: true,
        showInterfaces: true,
        showModules: true,
        showProperties: true,
        showEvents: true,
        showOperators: true,
        showUnits: true,
        showValues: true,
        showConstants: true,
        showEnums: true,
        showEnumMembers: true,
        showColors: true,
        showFiles: true,
        showReferences: true,
        showFolders: true,
        showTypeParameters: true,
        showIssues: true,
        showUsers: true
      }
    });

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Prevent default save behavior and trigger run if available
      if (onRun && !readOnly) {
        onRun();
      }
      return null;
    });

    // Add run shortcut
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onRun && !readOnly) {
        onRun();
      }
      return null;
    });

    // Add fullscreen toggle
    editor.addCommand(monaco.KeyCode.F11, () => {
      setIsFullscreen(!isFullscreen);
      return null;
    });

    // Enhanced auto-completion for common patterns
    monaco.languages.registerCompletionItemProvider(CodingService.getMonacoLanguage(language), {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = getLanguageSpecificSuggestions(language, model, position);
        return { suggestions };
      }
    });

    // Add code formatting
    monaco.languages.registerDocumentFormattingEditProvider(CodingService.getMonacoLanguage(language), {
      provideDocumentFormattingEdits: (model: any) => {
        // Basic formatting - in a real implementation, you'd use language-specific formatters
        return [];
      }
    });

    // Add hover information
    monaco.languages.registerHoverProvider(CodingService.getMonacoLanguage(language), {
      provideHover: (model: any, position: any) => {
        const word = model.getWordAtPosition(position);
        if (word) {
          return {
            range: new monaco.Range(position.lineNumber, word.startColumn, position.lineNumber, word.endColumn),
            contents: [
              { value: `**${word.word}**` },
              { value: getHoverInfo(word.word, language) }
            ]
          };
        }
        return null;
      }
    });
  };

  const getLanguageSpecificSuggestions = (lang: LanguageType, model?: any, position?: any) => {
    const commonSuggestions = [
      {
        label: 'for',
        kind: 14, // Snippet
        insertText: lang === 'python' ? 'for ${1:i} in range(${2:n}):\n    ${3:pass}' : 'for (${1:int i = 0}; ${1:i} < ${2:n}; ${1:i}++) {\n    ${3:// code here}\n}',
        insertTextRules: 4, // InsertAsSnippet
        documentation: 'For loop',
        detail: 'For loop snippet'
      },
      {
        label: 'if',
        kind: 14,
        insertText: lang === 'python' ? 'if ${1:condition}:\n    ${2:pass}' : 'if (${1:condition}) {\n    ${2:// code here}\n}',
        insertTextRules: 4,
        documentation: 'If statement',
        detail: 'If statement snippet'
      }
    ];

    switch (lang) {
      case 'python':
        return [
          ...commonSuggestions,
          {
            label: 'def',
            kind: 14,
            insertText: 'def ${1:function_name}(${2:args}):\n    """${3:Description}\n    \n    Args:\n        ${2:args}: ${4:Description}\n    \n    Returns:\n        ${5:Description}\n    """\n    ${6:pass}',
            insertTextRules: 4,
            documentation: 'Function definition with docstring',
            detail: 'Function with documentation'
          },
          {
            label: 'class',
            kind: 14,
            insertText: 'class ${1:ClassName}:\n    """${2:Class description}"""\n    \n    def __init__(self${3:, args}):\n        """Initialize ${1:ClassName}\n        \n        Args:\n            ${3:args}: ${4:Description}\n        """\n        ${5:pass}',
            insertTextRules: 4,
            documentation: 'Class definition with docstring',
            detail: 'Class with documentation'
          },
          {
            label: 'try',
            kind: 14,
            insertText: 'try:\n    ${1:# code that might raise an exception}\nfinally:\n    ${2:# cleanup code}',
            insertTextRules: 4,
            documentation: 'Try-except block',
            detail: 'Exception handling'
          },
          {
            label: 'list_comp',
            kind: 14,
            insertText: '[${1:expression} for ${2:item} in ${3:iterable} if ${4:condition}]',
            insertTextRules: 4,
            documentation: 'List comprehension',
            detail: 'List comprehension pattern'
          }
        ];
      case 'java':
        return [
          ...commonSuggestions,
          {
            label: 'public static void main',
            kind: 14,
            insertText: 'public static void main(String[] args) {\n    ${1:// code here}\n}',
            insertTextRules: 4,
            documentation: 'Main method',
            detail: 'Application entry point'
          },
          {
            label: 'class',
            kind: 14,
            insertText: 'public class ${1:ClassName} {\n    ${2:// class members}\n}',
            insertTextRules: 4,
            documentation: 'Class definition',
            detail: 'Public class'
          },
          {
            label: 'method',
            kind: 14,
            insertText: 'public ${1:returnType} ${2:methodName}(${3:parameters}) {\n    ${4:// method body}\n    return ${5:value};\n}',
            insertTextRules: 4,
            documentation: 'Method definition',
            detail: 'Public method'
          },
          {
            label: 'try',
            kind: 14,
            insertText: 'try {\n    ${1:// code that might throw exception}\n} catch (${2:Exception} e) {\n    ${3:// handle exception}\n}',
            insertTextRules: 4,
            documentation: 'Try-catch block',
            detail: 'Exception handling'
          }
        ];
      case 'cpp':
        return [
          ...commonSuggestions,
          {
            label: 'main',
            kind: 14,
            insertText: 'int main() {\n    ${1:// code here}\n    return 0;\n}',
            insertTextRules: 4,
            documentation: 'Main function',
            detail: 'Program entry point'
          },
          {
            label: 'class',
            kind: 14,
            insertText: 'class ${1:ClassName} {\npublic:\n    ${1:ClassName}();\n    ~${1:ClassName}();\n    \nprivate:\n    ${2:// private members}\n};',
            insertTextRules: 4,
            documentation: 'Class definition',
            detail: 'C++ class with constructor and destructor'
          },
          {
            label: 'vector',
            kind: 14,
            insertText: 'std::vector<${1:int}> ${2:vec}${3: = {${4:values}}};',
            insertTextRules: 4,
            documentation: 'Vector declaration',
            detail: 'STL vector'
          },
          {
            label: 'algorithm',
            kind: 14,
            insertText: 'std::${1:sort}(${2:container}.begin(), ${2:container}.end());',
            insertTextRules: 4,
            documentation: 'STL algorithm',
            detail: 'Standard algorithm usage'
          }
        ];
      case 'javascript':
        return [
          ...commonSuggestions,
          {
            label: 'function',
            kind: 14,
            insertText: 'function ${1:functionName}(${2:args}) {\n    ${3:// code here}\n    return ${4:value};\n}',
            insertTextRules: 4,
            documentation: 'Function declaration',
            detail: 'Function with return'
          },
          {
            label: 'arrow',
            kind: 14,
            insertText: 'const ${1:functionName} = (${2:args}) => {\n    ${3:// code here}\n    return ${4:value};\n};',
            insertTextRules: 4,
            documentation: 'Arrow function',
            detail: 'ES6 arrow function'
          },
          {
            label: 'async',
            kind: 14,
            insertText: 'async function ${1:functionName}(${2:args}) {\n    try {\n        const ${3:result} = await ${4:promise};\n        return ${3:result};\n    } catch (error) {\n        ${5:// handle error}\n    }\n}',
            insertTextRules: 4,
            documentation: 'Async function',
            detail: 'Async/await pattern'
          },
          {
            label: 'class',
            kind: 14,
            insertText: 'class ${1:ClassName} {\n    constructor(${2:args}) {\n        ${3:// initialization}\n    }\n    \n    ${4:methodName}() {\n        ${5:// method body}\n    }\n}',
            insertTextRules: 4,
            documentation: 'ES6 class',
            detail: 'Class with constructor and method'
          }
        ];
      default:
        return commonSuggestions;
    }
  };

  const getHoverInfo = (word: string, lang: LanguageType): string => {
    const commonKeywords: Record<string, string> = {
      'for': 'Iteration statement that repeats a block of code',
      'if': 'Conditional statement that executes code based on a condition',
      'while': 'Loop that continues while a condition is true',
      'function': 'Reusable block of code that performs a specific task',
      'return': 'Statement that exits a function and optionally returns a value'
    };

    const languageSpecific: Record<LanguageType, Record<string, string>> = {
      python: {
        'def': 'Defines a function in Python',
        'class': 'Defines a class in Python',
        'import': 'Imports modules or specific functions',
        'len': 'Returns the length of an object',
        'range': 'Generates a sequence of numbers',
        'print': 'Outputs text to the console'
      },
      java: {
        'public': 'Access modifier that makes members accessible from anywhere',
        'private': 'Access modifier that restricts access to the same class',
        'static': 'Keyword that makes members belong to the class rather than instances',
        'void': 'Return type indicating the method returns no value',
        'String': 'Class representing a sequence of characters'
      },
      cpp: {
        'int': 'Integer data type',
        'std': 'Standard namespace containing C++ standard library',
        'vector': 'Dynamic array container from STL',
        'cout': 'Standard output stream object',
        'endl': 'Inserts a newline and flushes the output buffer'
      },
      javascript: {
        'const': 'Declares a constant variable that cannot be reassigned',
        'let': 'Declares a block-scoped variable',
        'var': 'Declares a function-scoped variable',
        'async': 'Declares an asynchronous function',
        'await': 'Waits for a Promise to resolve'
      }
    };

    return languageSpecific[lang]?.[word] || commonKeywords[word] || `${word} - ${lang} keyword or identifier`;
  };

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(value);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleFormatCode = () => {
    if (editorRef.current) {
      editorRef.current.getAction('editor.action.formatDocument').run();
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const toggleTheme = () => {
    setCurrentTheme(currentTheme === 'light' ? 'dark' : 'light');
  };

  const handleFontSizeChange = (newSize: number) => {
    setFontSize(newSize);
    if (editorRef.current) {
      editorRef.current.updateOptions({ fontSize: newSize });
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChange(value);
    }
  };

  return (
    <div className={`${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'relative'} border border-gray-300 rounded-lg overflow-hidden`}>
      {/* Toolbar */}
      {showToolbar && (
        <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">
              {CodingService.getLanguageDisplayName(language)}
            </span>
            <div className="h-4 w-px bg-gray-300"></div>
            <span className="text-xs text-gray-500">
              {value.split('\n').length} lines
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Font Size Controls */}
            <div className="flex items-center space-x-1">
              <button
                onClick={() => handleFontSizeChange(Math.max(10, fontSize - 1))}
                className="p-1 text-gray-500 hover:text-gray-700"
                title="Decrease font size"
              >
                <span className="text-xs">A-</span>
              </button>
              <span className="text-xs text-gray-500 min-w-[2rem] text-center">{fontSize}px</span>
              <button
                onClick={() => handleFontSizeChange(Math.min(24, fontSize + 1))}
                className="p-1 text-gray-500 hover:text-gray-700"
                title="Increase font size"
              >
                <span className="text-xs">A+</span>
              </button>
            </div>

            <div className="h-4 w-px bg-gray-300"></div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-1.5 text-gray-500 hover:text-gray-700 rounded"
              title="Toggle theme"
            >
              {currentTheme === 'light' ? (
                <MoonIcon className="h-4 w-4" />
              ) : (
                <SunIcon className="h-4 w-4" />
              )}
            </button>

            {/* Copy Code */}
            <button
              onClick={handleCopyCode}
              className="p-1.5 text-gray-500 hover:text-gray-700 rounded"
              title="Copy code"
            >
              <DocumentDuplicateIcon className="h-4 w-4" />
            </button>

            {/* Format Code */}
            {!readOnly && (
              <button
                onClick={handleFormatCode}
                className="p-1.5 text-gray-500 hover:text-gray-700 rounded"
                title="Format code (Shift+Alt+F)"
              >
                <CogIcon className="h-4 w-4" />
              </button>
            )}

            {/* Run Code */}
            {onRun && !readOnly && (
              <button
                onClick={onRun}
                disabled={isRunning}
                className="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Run code (Ctrl+Enter)"
              >
                {isRunning ? (
                  <>
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></div>
                    Running
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-3 w-3 mr-1" />
                    Run
                  </>
                )}
              </button>
            )}

            {/* Fullscreen Toggle */}
            <button
              onClick={toggleFullscreen}
              className="p-1.5 text-gray-500 hover:text-gray-700 rounded"
              title="Toggle fullscreen (F11)"
            >
              {isFullscreen ? (
                <ArrowsPointingInIcon className="h-4 w-4" />
              ) : (
                <ArrowsPointingOutIcon className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      )}

      {/* Editor */}
      <div className={isFullscreen ? 'h-[calc(100vh-60px)]' : ''}>
        <Editor
          height={isFullscreen ? '100%' : height}
          language={CodingService.getMonacoLanguage(language)}
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={currentTheme === 'dark' ? 'vs-dark' : 'vs'}
          options={{
            readOnly,
            fontSize,
            minimap: { enabled: true, scale: 1 },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: language === 'python' ? 4 : 2,
            insertSpaces: true,
            wordWrap: 'on',
            lineNumbers: 'on',
            glyphMargin: true,
            folding: true,
            lineDecorationsWidth: 10,
            lineNumbersMinChars: 3,
            renderLineHighlight: 'line',
            selectOnLineNumbers: true,
            roundedSelection: false,
            cursorStyle: 'line',
            bracketPairColorization: { enabled: true },
            guides: {
              bracketPairs: true,
              indentation: true
            }
          }}
        />
      </div>

      {/* Keyboard Shortcuts Help */}
      {isFullscreen && (
        <div className="absolute bottom-4 right-4 bg-black bg-opacity-75 text-white text-xs p-2 rounded">
          <div>Ctrl+S / Ctrl+Enter: Run</div>
          <div>F11: Exit Fullscreen</div>
          <div>Shift+Alt+F: Format</div>
        </div>
      )}
    </div>
  );
};

export default CodeEditor;