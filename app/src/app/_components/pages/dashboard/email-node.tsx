import React, { type FC } from 'react';
import { Handle, type NodeProps, Position } from '@xyflow/react';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../ui/tooltip';

const EmailNode: FC<NodeProps> = (({ isConnectable, data }) => {
    const onClick = data.onClick as ((data: Record<string, unknown>) => void) | undefined

    return (
        <Tooltip>
            <TooltipTrigger>
                <div
                    onClick={() => {
                        if (onClick) onClick(data)
                    }}
                    className='w-[150px] aspect-square relative flex items-center justify-center bg-gray-900/50 hover:bg-gray-800/50 backdrop-blur-lg duration-300 border-2 border-white rounded-full'>
                    <div className='absolute opacity-0'>
                        <Handle
                            id="src"
                            type="source"
                            position={Position.Top}
                            isConnectable={isConnectable}
                        />
                        <Handle
                            id="dst"
                            type="target"
                            position={Position.Top}
                            isConnectable={isConnectable}
                        />
                    </div>
                    <p className='px-3 w-full text-center drop-shadow-[0_1.8px_1.8px_rgba(0,0,0,0.8)]'>
                        {data.label as string}
                    </p>
                </div>
            </TooltipTrigger>
            <TooltipContent>
                <p>User with email: {data.label as string}</p>
            </TooltipContent>
        </Tooltip>
    );
});

export default EmailNode
