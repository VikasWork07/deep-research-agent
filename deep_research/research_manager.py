from agents import Agent, trace, Runner, gen_trace_id
import planner_agent
import asyncio
from planner_agent import planner_agent, WebSearchPlan, WebSearchItem
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from clarifier_agent import clarifier_agent, ClarifierOutput


class ResearchManager:
    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id= gen_trace_id()
        with trace("Research Manager", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield {"type":"trace", "content": f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n"}
            print("Analysing the research query for clarity...")
            clarifier_output = await self.clarifier_check(query)
            if clarifier_output.needs_clarification and clarifier_output.clarifying_questions:
                print("Query needs clarification. Asking user for clarification...")
                #yield "Query needs clarification...Please answer following questions to clarify your query:\n"
                #for q in clarifier_output.clarifying_questions:
                #    yield f"- {q}\n"
                yield {
                    "type": "clarification",
                    "content": clarifier_output.clarifying_questions,
                }
                return
            print("Starting research...")
            research_plan_response = await self.plan_searches(query)
            yield {"type":"status", "content": "Searched planned, starting to search...\n"}
            search_web_results = await self.search_web(research_plan_response)
            yield {"type":"status", "content": "Searches complete, writing report...\n"}
            report = await self.write_report(query, search_web_results)
            yield {"type":"status", "content": "Report writing complete...\n"}
            yield {"type":"report", "content": report.markdown_report}

    async def clarifier_check(self, query:str) -> ClarifierOutput:
        """Check if the query needs clarification and if so, returns questions to clarify the query"""
        clarifier_response = await Runner.run(clarifier_agent, query)
        return clarifier_response.final_output_as(ClarifierOutput)

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Started planning...")
        research_plan = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Planned number of searches: {len(research_plan.final_output.searches)}")
    
        return research_plan.final_output_as(WebSearchPlan)
    
    async def search_web(self, research_plan_response: WebSearchPlan) -> list[str]:
        """Run web searches in parallel and collect results"""
        async def _run_search(item):
            inp = f"Search term: {item.query}\nReason for searching: {item.reason}"
            try:
                resp = await Runner.run(search_agent, inp)
                return resp.final_output
            except Exception as e:
                return {"query": getattr(item, 'query', None), "error": str(e)}

        tasks = [asyncio.create_task(_run_search(item)) for item in research_plan_response.searches]
        search_results = []
        num_completed=0
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                search_results.append(result)
                num_completed +=1
            print(f"Searching....{num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return search_results
    
    async def write_report(self, query:str, search_results: list[str]) -> ReportData:
        """Writing a report based on the original query and search results"""
        inp = f"Original query: {query} \n Summarized search results: {search_results}"
        print("Thinking about how to write the report....")
        report = await Runner.run(writer_agent, inp)
        print("Finished writing report")
        return report.final_output_as(ReportData)
    
    async def send_email(self,query: str, report: ReportData):
        """Send the report via email using the email agent"""
        inp = f"Original Query: {query}\n Report summary: {report.short_summary}\n Full report: {report.markdown_report}"
        email_response = await Runner.run(email_agent, inp)
        return email_response.final_output