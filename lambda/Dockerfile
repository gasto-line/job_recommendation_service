FROM public.ecr.aws/lambda/python:3.13
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
RUN pip install supabase -t ${LAMBDA_TASK_ROOT}
CMD ["lambda_function.lambda_handler"]