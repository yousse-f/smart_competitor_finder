import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface ProgressBarProps {
  progress: number;
  label?: string;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  label,
  className = '' 
}) => {
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between text-sm text-slate-400 mb-2">
          <span>{label}</span>
          <span>{progress}%</span>
        </div>
      )}
      <div className="progress-bar">
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>
    </div>
  );
};

interface ProcessingStepsProps {
  steps: Array<{
    label: string;
    status: 'pending' | 'processing' | 'completed' | 'error';
  }>;
}

export const ProcessingSteps: React.FC<ProcessingStepsProps> = ({ steps }) => {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="flex items-center gap-3"
        >
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
            step.status === 'completed' ? 'bg-green-500 text-white' :
            step.status === 'processing' ? 'bg-blue-500 text-white' :
            step.status === 'error' ? 'bg-red-500 text-white' :
            'bg-slate-600 text-slate-400'
          }`}>
            {step.status === 'processing' ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : step.status === 'completed' ? (
              '✓'
            ) : step.status === 'error' ? (
              '✕'
            ) : (
              index + 1
            )}
          </div>
          <span className={`text-sm ${
            step.status === 'completed' ? 'text-green-400' :
            step.status === 'processing' ? 'text-blue-400' :
            step.status === 'error' ? 'text-red-400' :
            'text-slate-400'
          }`}>
            {step.label}
          </span>
        </motion.div>
      ))}
    </div>
  );
};

interface DataTableProps {
  columns: Array<{
    key: string;
    label: string;
    width?: string;
  }>;
  data: any[];
  renderCell?: (key: string, value: any, row: any) => React.ReactNode;
}

export const DataTable: React.FC<DataTableProps> = ({ 
  columns, 
  data, 
  renderCell 
}) => {
  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} style={{ width: column.width }}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <motion.tr
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {columns.map((column) => (
                <td key={column.key}>
                  {renderCell ? 
                    renderCell(column.key, row[column.key], row) : 
                    row[column.key]
                  }
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};